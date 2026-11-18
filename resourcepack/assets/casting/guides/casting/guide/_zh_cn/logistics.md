---
navigation:
    title: 物流
    icon: 'casting:controller'
    parent: index.md
    position: 5
---

# 物流

## 物流

Casting 的方块之间会自动推送和抽取流体。

## 方向
- 控制器会将输出储罐中的流体推送到相邻的固化器和混合器
- 固化器会从相邻的控制器和混合器（输出储罐）接收流体
- 混合器会从相邻的控制器接收流体

## 示例
<GameScene zoom="3" interactive={true}>
  <ImportStructure src="assets/structures/logistics.nbt" />
</GameScene>
控制器正将流体推送到右侧的固化器和上方的混合器，混合器随后将自己的输出推送到右侧的固化器。

## 管道
也可以使用管道在方块之间传输流体和物品；Pipez、BBL Routers 等大多数管道都能与方块的过滤系统配合使用。

### 疑难解答
如果流体没有被推送或抽取，请确认方块彼此相邻，且负责推送的方块，其输出储罐能够容纳该流体。
