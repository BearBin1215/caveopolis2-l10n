"""修补 strainers 的矿石碎块名称，并补充对应的语言键。

OrePieceItem#getName 把 ore_type 组件值直接拼成字符串传入 %s，资源包无法翻译。
这里把该方法改为查找 item.strainers.ore_piece.<ore_type>，并在构建时替换类文件。
"""

from __future__ import annotations

import hashlib
import io
import struct
import zipfile
from pathlib import Path

from common import ROOT, find_jar

CLASS_ENTRY = "com/benbenlaw/strainers/item/OrePieceItem.class"
METHOD_NAME = "getName"
METHOD_DESC = "(Lnet/minecraft/world/item/ItemStack;)Lnet/minecraft/network/chat/Component;"
SOURCE_SHA1 = "77b9aaaa1a08e12741f99031b3028778c8ac5348"

# 当前整合包实际出现的矿石类型。翻译沿用 glossary 与 i18n 资源包中的材料名。
ORE_NAMES: dict[str, tuple[str, str]] = {
    "aluminum": ("Aluminum", "铝"),
    "cinnabar": ("Cinnabar", "朱砂"),
    "coal": ("Coal", "煤炭"),
    "copper": ("Copper", "铜"),
    "diamond": ("Diamond", "钻石"),
    "dimensional": ("Dimensional", "维度"),
    "emerald": ("Emerald", "绿宝石"),
    "ender_pearl": ("Ender Pearl", "末影珍珠"),
    "fluorite": ("Fluorite", "氟石"),
    "gold": ("Gold", "金"),
    "inferium": ("Inferium", "下级精华"),
    "iridium": ("Iridium", "铱"),
    "iron": ("Iron", "铁"),
    "lapis": ("Lapis", "青金石"),
    "lead": ("Lead", "铅"),
    "netherite_scrap": ("Netherite Scrap", "下界合金碎片"),
    "nickel": ("Nickel", "镍"),
    "osmium": ("Osmium", "锇"),
    "peridot": ("Peridot", "橄榄石"),
    "platinum": ("Platinum", "铂"),
    "prosperity": ("Prosperity", "活化水晶"),
    "quartz": ("Quartz", "石英"),
    "redstone": ("Redstone", "红石"),
    "ruby": ("Ruby", "红宝石"),
    "salt": ("Salt", "盐"),
    "sapphire": ("Sapphire", "蓝宝石"),
    "silver": ("Silver", "银"),
    "soulium": ("Soulium", "离魂"),
    "sulfur": ("Sulfur", "硫磺"),
    "tin": ("Tin", "锡"),
    "uraninite": ("Uraninite", "晶质铀"),
    "uraninite_dense": ("Uraninite Dense", "致密晶质铀"),
    "uraninite_poor": ("Uraninite Poor", "贫瘠晶质铀"),
    "uraninite_regular": ("Uraninite Regular", "普通晶质铀"),
    "uranium": ("Uranium", "铀"),
    "zinc": ("Zinc", "锌"),
}

# 这些译文包含术语表禁用的子串，单独给出完整名称。
ORE_FULL_ZH = {
    "netherite_scrap": "下界合金碎片矿石碎块",
    "uraninite": "晶质铀碎块",
    "uraninite_dense": "致密晶质铀碎块",
    "uraninite_poor": "贫瘠晶质铀碎块",
    "uraninite_regular": "普通晶质铀碎块",
}


def _key(ore: str) -> str:
    return f"item.strainers.ore_piece.{ore}"


def extra_en() -> dict[str, str]:
    return {
        _key(ore): f"{english} Ore Piece"
        for ore, (english, _) in sorted(ORE_NAMES.items())
    }


def extra_zh() -> dict[str, str]:
    return {
        _key(ore): ORE_FULL_ZH.get(ore, f"{chinese}矿石碎块")
        for ore, (_, chinese) in sorted(ORE_NAMES.items())
    }


def _u2(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from(">H", data, offset)[0]


def _u4(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def _u2b(value: int) -> bytes:
    return struct.pack(">H", value)


def _read_pool(data: bytes | bytearray) -> tuple[dict[int, dict], int]:
    count = _u2(data, 8)
    offset = 10
    entries: dict[int, dict] = {}
    index = 1
    while index < count:
        tag = data[offset]
        offset += 1
        if tag == 1:
            length = _u2(data, offset)
            length_offset = offset
            offset += 2
            text = bytes(data[offset : offset + length]).decode("utf-8")
            entries[index] = {
                "tag": 1,
                "text": text,
                "length_off": length_offset,
                "data_off": offset,
            }
            offset += length
        elif tag in (3, 4):
            entries[index] = {"tag": tag}
            offset += 4
        elif tag in (5, 6):
            entries[index] = {"tag": tag}
            offset += 8
            index += 1
        elif tag in (7, 8, 16, 19, 20):
            entries[index] = {"tag": tag, "ref": _u2(data, offset)}
            offset += 2
        elif tag in (9, 10, 11, 12, 17, 18):
            entries[index] = {
                "tag": tag,
                "ref1": _u2(data, offset),
                "ref2": _u2(data, offset + 2),
            }
            offset += 4
        elif tag == 15:
            entries[index] = {
                "tag": tag,
                "ref1": data[offset],
                "ref2": _u2(data, offset + 1),
            }
            offset += 3
        else:
            raise ValueError(f"未知常量池标签 {tag}（索引 {index}）")
        index += 1
    return entries, offset


def _utf8(pool: dict[int, dict], index: int) -> str:
    entry = pool[index]
    if entry["tag"] != 1:
        raise ValueError(f"常量 {index} 不是 UTF8")
    return entry["text"]


def _class_name(pool: dict[int, dict], index: int) -> str:
    entry = pool[index]
    if entry["tag"] != 7:
        raise ValueError(f"常量 {index} 不是类")
    return _utf8(pool, entry["ref"])


def _name_and_type(pool: dict[int, dict], index: int) -> tuple[str, str]:
    entry = pool[index]
    if entry["tag"] != 12:
        raise ValueError(f"常量 {index} 不是 NameAndType")
    return _utf8(pool, entry["ref1"]), _utf8(pool, entry["ref2"])


def _find_utf8(pool: dict[int, dict], text: str) -> int:
    matches = [index for index, entry in pool.items() if entry["tag"] == 1 and entry["text"] == text]
    if len(matches) != 1:
        raise ValueError(f"UTF8 常量 {text!r} 出现 {len(matches)} 次")
    return matches[0]


def _find_class(pool: dict[int, dict], name: str) -> int:
    matches = [
        index
        for index, entry in pool.items()
        if entry["tag"] == 7 and _class_name(pool, index) == name
    ]
    if len(matches) != 1:
        raise ValueError(f"类常量 {name} 出现 {len(matches)} 次")
    return matches[0]


def _find_string(pool: dict[int, dict], text: str) -> int:
    matches = [
        index
        for index, entry in pool.items()
        if entry["tag"] == 8 and _utf8(pool, entry["ref"]) == text
    ]
    if len(matches) != 1:
        raise ValueError(f"字符串常量 {text!r} 出现 {len(matches)} 次")
    return matches[0]


def _find_method(
    pool: dict[int, dict], owner: str, name: str, descriptor: str
) -> int:
    matches = []
    for index, entry in pool.items():
        if entry["tag"] not in (10, 11):
            continue
        if _class_name(pool, entry["ref1"]) != owner:
            continue
        if _name_and_type(pool, entry["ref2"]) == (name, descriptor):
            matches.append(index)
    if len(matches) != 1:
        raise ValueError(f"方法 {owner}.{name}{descriptor} 出现 {len(matches)} 次")
    return matches[0]


def _replace_same_length(data: bytearray, pool: dict[int, dict], index: int, text: str) -> None:
    entry = pool[index]
    old = entry["text"].encode("utf-8")
    new = text.encode("utf-8")
    if len(old) != len(new):
        raise ValueError(f"UTF8 常量长度不一致：{entry['text']!r} -> {text!r}")
    start = entry["data_off"]
    data[start : start + len(old)] = new


def _patch_class(data: bytes) -> bytes:
    if _u4(data, 0) != 0xCAFEBABE:
        raise ValueError("不是 class 文件")
    pool, _ = _read_pool(data)

    prefix_utf8 = _find_utf8(pool, "item.strainers.ore_piece")
    prefix_string = _find_string(pool, "item.strainers.ore_piece")
    upper_utf8 = _find_utf8(pool, "toUpperCase")
    space_utf8 = _find_utf8(pool, " ")
    space_string = _find_string(pool, " ")

    if [i for i, e in pool.items() if e["tag"] == 8 and e["ref"] == space_utf8] != [space_string]:
        raise ValueError("空格字符串常量被多处引用")
    upper_refs = [i for i, e in pool.items() if e["tag"] == 12 and e["ref1"] == upper_utf8]
    if len(upper_refs) != 1:
        raise ValueError("toUpperCase 常量被多处引用")

    mutable = bytearray(data)
    _replace_same_length(mutable, pool, upper_utf8, "toLowerCase")
    _replace_same_length(mutable, pool, space_utf8, "_")

    old_prefix = "item.strainers.ore_piece"
    new_prefix = "item.strainers.ore_piece."
    entry = pool[prefix_utf8]
    old_bytes = old_prefix.encode("utf-8")
    new_bytes = new_prefix.encode("utf-8")
    mutable[entry["length_off"] : entry["length_off"] + 2] = _u2b(len(new_bytes))
    mutable[entry["data_off"] : entry["data_off"] + len(old_bytes)] = new_bytes

    pool, pool_end = _read_pool(mutable)
    code_name = _find_utf8(pool, "Code")
    string_builder = _find_class(pool, "java/lang/StringBuilder")
    init_method = _find_method(
        pool, "java/lang/StringBuilder", "<init>", "()V"
    )
    append_method = _find_method(
        pool,
        "java/lang/StringBuilder",
        "append",
        "(Ljava/lang/String;)Ljava/lang/StringBuilder;",
    )
    tostring_method = _find_method(
        pool, "java/lang/StringBuilder", "toString", "()Ljava/lang/String;"
    )
    translatable_method = _find_method(
        pool,
        "net/minecraft/network/chat/Component",
        "translatable",
        "(Ljava/lang/String;)Lnet/minecraft/network/chat/MutableComponent;",
    )

    offset = pool_end + 6
    interfaces = _u2(mutable, offset)
    offset += 2 + 2 * interfaces
    fields = _u2(mutable, offset)
    offset += 2
    for _ in range(fields):
        attributes = _u2(mutable, offset + 6)
        offset += 8
        for _ in range(attributes):
            length = _u4(mutable, offset + 2)
            offset += 6 + length

    methods = _u2(mutable, offset)
    offset += 2
    target: tuple[int, int, int] | None = None
    for _ in range(methods):
        name_index = _u2(mutable, offset + 2)
        descriptor_index = _u2(mutable, offset + 4)
        attributes = _u2(mutable, offset + 6)
        offset += 8
        for _ in range(attributes):
            attribute_name = _u2(mutable, offset)
            attribute_length = _u4(mutable, offset + 2)
            if (
                attribute_name == code_name
                and _utf8(pool, name_index) == METHOD_NAME
                and _utf8(pool, descriptor_index) == METHOD_DESC
            ):
                target = (offset, offset + 6, attribute_length)
            offset += 6 + attribute_length

    if target is None:
        raise ValueError("找不到 OrePieceItem#getName")
    attribute_offset, body_offset, body_length = target
    max_stack = _u2(mutable, body_offset)
    max_locals = _u2(mutable, body_offset + 2)
    code_length = _u4(mutable, body_offset + 4)
    code_start = body_offset + 8
    code = bytes(mutable[code_start : code_start + code_length])
    # 121 是循环结束、原方法拼接 %s 参数的位置，138 是 areturn；前面的循环保持不变。
    if code_length != 139 or code[121] != 0x12 or code[122] != prefix_string:
        raise ValueError("getName 的字节码与预期不一致")

    exception_count = _u2(mutable, code_start + code_length)
    exception_start = code_start + code_length + 2
    exception_bytes = bytes(
        mutable[exception_start : exception_start + 8 * exception_count]
    )
    sub_start = exception_start + 8 * exception_count
    sub_count = _u2(mutable, sub_start)
    sub_offset = sub_start + 2
    keep: list[tuple[int, bytes]] = []
    for _ in range(sub_count):
        name = _u2(mutable, sub_offset)
        length = _u4(mutable, sub_offset + 2)
        data_start = sub_offset + 6
        if _utf8(pool, name) == "StackMapTable":
            keep.append((name, bytes(mutable[data_start : data_start + length])))
        sub_offset = data_start + length
    if not keep:
        raise ValueError("getName 缺少 StackMapTable")

    tail = (
        bytes([0xBB])
        + _u2b(string_builder)
        + bytes([0x59, 0xB7])
        + _u2b(init_method)
        + bytes([0x13])
        + _u2b(prefix_string)
        + bytes([0xB6])
        + _u2b(append_method)
        + bytes([0x19, 0x04, 0xB6])
        + _u2b(tostring_method)
        + bytes([0xB6])
        + _u2b(append_method)
        + bytes([0xB6])
        + _u2b(tostring_method)
        + bytes([0xB8])
        + _u2b(translatable_method)
        + bytes([0xB0])
    )
    new_code = code[:121] + tail
    body = (
        struct.pack(">HHI", max(max_stack, 3), max_locals, len(new_code))
        + new_code
        + struct.pack(">H", exception_count)
        + exception_bytes
        + struct.pack(">H", len(keep))
    )
    for name, payload in keep:
        body += struct.pack(">HI", name, len(payload)) + payload

    result = (
        mutable[:attribute_offset]
        + struct.pack(">HI", code_name, len(body))
        + body
        + mutable[body_offset + body_length :]
    )
    return bytes(result)


def patched_jar_bytes(source: Path) -> bytes:
    digest = hashlib.sha1(source.read_bytes()).hexdigest()
    if digest != SOURCE_SHA1:
        raise ValueError(
            f"{source.name} 的 SHA1 为 {digest}，预期 {SOURCE_SHA1}；"
            "模组版本已变化，需要重新核对补丁"
        )
    with zipfile.ZipFile(source) as archive:
        original = archive.read(CLASS_ENTRY)
    patched = _patch_class(original)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        with zipfile.ZipFile(source) as source_archive:
            for info in source_archive.infolist():
                payload = (
                    patched
                    if info.filename == CLASS_ENTRY
                    else source_archive.read(info.filename)
                )
                archive.writestr(info, payload)
    return buffer.getvalue()


def write_patched_jar(target: Path, source: Path | None = None) -> Path:
    source = source or find_jar("strainers")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(patched_jar_bytes(source))
    return target


if __name__ == "__main__":
    jar = find_jar("strainers")
    output = ROOT / "dist" / "strainers-patched.jar"
    write_patched_jar(output, jar)
    print(f"已生成 {output}")