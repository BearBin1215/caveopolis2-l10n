"""解析 FTB Quests 使用的 JSON5 子集。"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class JSON5Error(ValueError):
    pass


_NUMBER = re.compile(r"[+-]?(?:0[xX][0-9a-fA-F]+|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)")
_IDENT = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
_ESCAPES = {
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "0": "\0",
    "'": "'",
    '"': '"',
    "\\": "\\",
    "/": "/",
}


class _Parser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.length = len(text)

    def error(self, message: str) -> JSON5Error:
        line = self.text.count("\n", 0, self.pos) + 1
        column = self.pos - self.text.rfind("\n", 0, self.pos)
        return JSON5Error(f"{message}（第 {line} 行第 {column} 列）")

    def skip(self) -> None:
        while self.pos < self.length:
            char = self.text[self.pos]
            if char in " \t\r\n\ufeff":
                self.pos += 1
            elif self.text.startswith("//", self.pos):
                end = self.text.find("\n", self.pos)
                self.pos = self.length if end == -1 else end + 1
            elif self.text.startswith("/*", self.pos):
                end = self.text.find("*/", self.pos + 2)
                if end == -1:
                    raise self.error("注释没有结束")
                self.pos = end + 2
            else:
                return

    def parse(self) -> Any:
        self.skip()
        value = self.value()
        self.skip()
        if self.pos != self.length:
            raise self.error("根节点之后还有内容")
        return value

    def value(self) -> Any:
        self.skip()
        if self.pos >= self.length:
            raise self.error("缺少值")
        char = self.text[self.pos]
        if char == "{":
            return self.object()
        if char == "[":
            return self.array()
        if char in "\"'":
            return self.string()
        match = _NUMBER.match(self.text, self.pos)
        if match:
            self.pos = match.end()
            raw = match.group(0)
            if raw.lower().startswith(("0x", "+0x", "-0x")):
                return int(raw, 16)
            if any(c in raw for c in ".eE"):
                return float(raw)
            return int(raw)
        match = _IDENT.match(self.text, self.pos)
        if match:
            self.pos = match.end()
            word = match.group(0)
            if word == "true":
                return True
            if word == "false":
                return False
            if word == "null":
                return None
            if word in ("Infinity", "NaN"):
                return float(word)
            raise self.error(f"无法识别的值 {word}")
        raise self.error(f"无法识别的字符 {char}")

    def object(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        self.pos += 1
        self.skip()
        if self.pos < self.length and self.text[self.pos] == "}":
            self.pos += 1
            return result
        while True:
            self.skip()
            if self.pos >= self.length:
                raise self.error("对象没有结束")
            char = self.text[self.pos]
            if char in "\"'":
                key = self.string()
            else:
                match = _IDENT.match(self.text, self.pos)
                if not match:
                    raise self.error("对象的键无效")
                key = match.group(0)
                self.pos = match.end()
            self.skip()
            if self.pos >= self.length or self.text[self.pos] != ":":
                raise self.error("对象的键之后缺少冒号")
            self.pos += 1
            result[key] = self.value()
            self.skip()
            if self.pos >= self.length:
                raise self.error("对象没有结束")
            char = self.text[self.pos]
            if char == ",":
                self.pos += 1
                self.skip()
                if self.pos < self.length and self.text[self.pos] == "}":
                    self.pos += 1
                    return result
                continue
            if char == "}":
                self.pos += 1
                return result
            raise self.error("对象的成员之间缺少逗号")

    def array(self) -> list[Any]:
        result: list[Any] = []
        self.pos += 1
        self.skip()
        if self.pos < self.length and self.text[self.pos] == "]":
            self.pos += 1
            return result
        while True:
            result.append(self.value())
            self.skip()
            if self.pos >= self.length:
                raise self.error("数组没有结束")
            char = self.text[self.pos]
            if char == ",":
                self.pos += 1
                self.skip()
                if self.pos < self.length and self.text[self.pos] == "]":
                    self.pos += 1
                    return result
                continue
            if char == "]":
                self.pos += 1
                return result
            raise self.error("数组的元素之间缺少逗号")

    def string(self) -> str:
        quote = self.text[self.pos]
        self.pos += 1
        chars: list[str] = []
        while True:
            if self.pos >= self.length:
                raise self.error("字符串没有结束")
            char = self.text[self.pos]
            if char == quote:
                self.pos += 1
                return "".join(chars)
            if char == "\\":
                self.pos += 1
                if self.pos >= self.length:
                    raise self.error("转义没有结束")
                esc = self.text[self.pos]
                if esc in _ESCAPES:
                    chars.append(_ESCAPES[esc])
                    self.pos += 1
                elif esc == "u":
                    code = self.text[self.pos + 1 : self.pos + 5]
                    if len(code) != 4:
                        raise self.error("Unicode 转义无效")
                    chars.append(chr(int(code, 16)))
                    self.pos += 5
                elif esc == "x":
                    code = self.text[self.pos + 1 : self.pos + 3]
                    if len(code) != 2:
                        raise self.error("十六进制转义无效")
                    chars.append(chr(int(code, 16)))
                    self.pos += 3
                elif esc == "\r":
                    self.pos += 1
                    if self.pos < self.length and self.text[self.pos] == "\n":
                        self.pos += 1
                elif esc == "\n":
                    self.pos += 1
                else:
                    chars.append(esc)
                    self.pos += 1
            else:
                chars.append(char)
                self.pos += 1


def loads(text: str) -> Any:
    return _Parser(text).parse()


def load(path: str | Path) -> Any:
    return loads(Path(path).read_text(encoding="utf-8"))
