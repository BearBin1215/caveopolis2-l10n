---
navigation:
    title: 控制器
    icon: 'casting:controller'
    parent: index.md
    position: 10
item_ids:
    - 'casting:controller'

---

# 控制器

## 控制器

控制器是本模组的主要方块，物品会在这里熔化为对应的熔融形态。控制器接收到红石信号时会停止工作。

![示例](assets/controller_gui.png)

### 界面
左侧的 15 个槽位每个最多可放入 1 个物品，这些物品会被熔化为熔融形态。右侧较小的储罐是燃料储罐，显示相邻燃料储罐中的燃料。这些燃料用于熔化物品。旁边的 4 个较大储罐用于存放熔化后的产物。每个储罐只能容纳一种流体，任意两个储罐不会容纳相同的流体。界面上方会显示每个槽位的耗时。

<GameScene zoom="3" interactive={true}>
  <ImportStructure src="assets/structures/controller.nbt" />
</GameScene>

### 疑难解答
如果控制器没有熔化物品，请确认相邻储罐中的燃料温度足以熔化该物品。
