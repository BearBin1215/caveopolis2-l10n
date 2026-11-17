---
navigation:
    title: 跨维度激光器
    icon: 'dimresources:laser'
    parent: index.md
    position: 5
item_ids:
    - 'dimresources:laser'
---

# 跨维度激光器

## 激光器搭建

跨维度激光器用于开采其他行星上的方块。激光器必须放置在由维度石和维度石砖构成的结构上，示例如下。

<GameScene zoom="1" interactive={true}>
  <ImportStructure src="assets/structures/laser.nbt" />
</GameScene>

激光器需要在界面中放入一个行星定位器，以确定要从哪颗行星开采。

部分行星需要更高等级的激光器多方块结构。行星等级在 1 到 12 之间。每提升一级，多方块结构就需要增高 1 格。

<GameScene zoom="1" interactive={true}>
  <ImportStructure src="assets/structures/lasermax.nbt" />
</GameScene>
