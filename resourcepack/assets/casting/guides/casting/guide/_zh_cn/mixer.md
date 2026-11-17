---
navigation:
    title: 混合器
    icon: 'casting:mixer'
    parent: index.md
    position: 30
item_ids:
    - 'casting:mixer'

---

# 混合器

## 混合器

混合器用于将最多 4 种不同的流体混合成另一种流体。混合器接收到红石信号时会停止工作。

![示例](assets/mixer_gui.png)

### 界面
顶部的槽位是过滤槽，留空时允许任意流体进入下方的一个混合器储罐。要设置过滤，可以手持该流体的桶点击槽位，或从 JEI 中将流体拖到槽位上。过滤槽下方是 4 个输入储罐，右侧的储罐是输出储罐。

<GameScene zoom="3" interactive={true}>
  <ImportStructure src="assets/structures/mixer.nbt" />
</GameScene>

### 疑难解答
如果混合器没有进行混合，请确认用于混合的流体数量充足，并且输出储罐能够容纳产物流体。
