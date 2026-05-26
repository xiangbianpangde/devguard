# 测试规范

> 定义测试分层策略、编写标准、Mock 规则和覆盖率目标，确保测试有效、可维护、不成为负担。

---

## 适用范围

- **项目类型**：所有软件项目（前端/后端/全栈/移动端）
- **技术栈**：语言无关，示例以 Python（pytest）/ TypeScript（Jest）为主
- **团队规模**：1 人以上均适用

---

## 一、核心原则

### 原则 1：测试金字塔优先

单元测试多而快，集成测试居中，E2E 测试少而慢。投入产出比从金字塔底部到顶部递减。

**为什么**：单元测试毫秒级执行，能精确定位到函数级别的 bug。E2E 测试分钟级执行，失败时只知道"某处出问题了"。合理的比例（70% 单元 / 20% 集成 / 10% E2E）让 CI 跑得快、反馈精确。

### 原则 2：测试行为，不测试实现

测试用例验证"输入什么，得到什么"，而非"内部调用了哪个方法"。重构内部实现不应导致测试失败。

**为什么**：如果测试绑定了内部实现细节（如"调用了 `save_to_db()` 方法"），每次重构都会导致测试大面积失败，开发者最终会跳过测试。行为测试只关心结果，重构安全。

### 原则 3：一个测试只验证一件事

每个测试用例聚焦一个场景，失败时能从用例名称直接知道什么出了问题。

**为什么**：一个测试验证多个场景时，失败后需要逐行排查到底是哪个断言不通过。单一断言的测试失败即定位，排查效率提升一个数量级。

### 原则 4：Mock 第三方，不 Mock 自己

只为外部依赖（数据库、API、文件系统）创建 Mock，不对项目内部模块使用 Mock。过度 Mock 让测试变成"Mock 了自己"的虚假验证。

**为什么**：Mock 了内部模块后，测试通过不代表真实集成能工作。Mock 应该只隔离不可控的外部边界，内部模块的真实协作本身就是测试要保护的东西。

---

## 二、具体规则

### 2.1 测试金字塔

```
         /\
        /E2E\       少量，验证核心用户流程
       /------\
      /  集成  \     中量，验证模块间协作
     /----------\
    /   单元测试  \   大量，验证单一函数/方法
   /--------------\
```

| 层级 | 占比 | 执行速度 | 反馈粒度 | 维护成本 |
|------|------|---------|---------|---------|
| 单元测试 | ~70% | 毫秒级 | 函数/方法级 | 低 |
| 集成测试 | ~20% | 秒级 | 模块级 | 中 |
| E2E 测试 | ~10% | 分钟级 | 用户流程级 | 高 |

### 2.2 测试原则（FIRST）

| 原则 | 说明 |
|------|------|
| **F**ast | 快速执行，CI 中单元测试应 < 30 秒 |
| **I**ndependent | 独立运行，不依赖其他测试的执行顺序 |
| **R**epeatable | 可重复，每次运行结果一致（不依赖时间/网络/随机数） |
| **S**elf-validating | 自动判断通过/失败，不需要人工检查输出 |
| **T**imely | 及时编写，最好在实现代码前（TDD）或同步编写 |

### 2.3 什么需要测试

| 优先测试 | 可选测试 | 不需要测试 |
|---------|---------|-----------|
| 核心业务逻辑 | 简单 CRUD | 第三方库内部逻辑 |
| 复杂算法/计算 | 简单 getter/setter | 框架基础能力 |
| 边界条件（空值/零值/极大值） | UI 渲染细节 | 纯配置文件 |
| 异常路径（网络超时/数据库宕机） | 日志格式 | 自动生成的代码 |
| 安全相关代码 | | |

### 2.4 单元测试编写标准

**AAA 模式**：

```python
def test_calculate_discount_vip_user_gets_20_percent_off():
    # Arrange — 准备数据
    user = User(role="vip")
    order = Order(total=100.00)

    # Act — 执行被测方法
    result = calculate_discount(user, order)

    # Assert — 验证结果
    assert result == 80.00
```

**命名规范**：`test_<方法名>_<场景>_<期望结果>`

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| 测试命名描述意图 | 从名称能看出测什么、什么场景、期望什么 | 必须 |
| 一个测试一个断言 | 核心断言只有一个，辅助断言不超过 2 个 | 建议 |
| 禁止测试间共享状态 | 不用全局变量传递数据，每个测试自给自足 | 必须 |

### 2.5 Mock 策略

| 需要 Mock | 不需要 Mock | 原则 |
|-----------|------------|------|
| 外部 API 调用 | 纯函数 | 只 Mock 自己的依赖 |
| 数据库（单元测试中） | 简单数据结构 | 不过度 Mock |
| 文件系统操作 | 被测函数本身 | 验证 Mock 调用次数和参数 |
| 时间依赖（`datetime.now()`） | 值对象/实体 | |
| 随机函数 | | |

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| 只 Mock 外部边界 | 数据库、HTTP、消息队列、文件系统 | 必须 |
| 禁止 Mock 项目内部类 | 内部模块的真实协作是测试保护的对象 | 必须 |
| Mock 后验证交互参数 | `mock.assert_called_once_with(...)` | 建议 |

### 2.6 覆盖率目标

| 阶段 | 行覆盖率 | 分支覆盖率 |
|------|---------|-----------|
| 快速原型 | 不作要求 | 不作要求 |
| MVP | ≥ 60% | ≥ 50% |
| 正式产品 | ≥ 80% | ≥ 70% |
| 核心模块（支付/认证/数据安全） | ≥ 90% | ≥ 85% |

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| CI 中检查覆盖率 | 低于阈值阻止合入 | 建议 |
| 配置/常量/自动生成代码可排除 | 在覆盖率配置中显式声明排除范围 | 建议 |
| 覆盖率是下限不是目标 | 100% 覆盖率不代表 100% 正确；关注未覆盖分支的业务意义 | 建议 |

### 2.7 CI 集成

| 阶段 | 执行内容 | 通过条件 |
|------|---------|---------|
| pre-commit | 单元测试（< 30s） | 100% 通过 |
| PR | 全部单元 + 集成测试 + 覆盖率检查 | 100% 通过 + 覆盖率达标 |
| 发布前 | 全部测试 + 性能测试 + 安全扫描 | 全部通过 |

---

## 三、反模式

### ❌ 反模式 1：测试依赖执行顺序

```python
# test_user.py
def test_create_user():
    global test_user_id
    user = create_user("张三")
    test_user_id = user.id  # 写入全局变量
    assert user.name == "张三"

def test_update_user():
    # 依赖 test_create_user 先执行！
    user = update_user(test_user_id, name="李四")
    assert user.name == "李四"
```

**问题**：如果 `test_create_user` 失败或未执行，`test_update_user` 必然失败且错误信息不明确。单独运行 `test_update_user` 也会因 `test_user_id` 未定义而崩溃。

### ✅ 正确做法：每个测试自给自足

```python
def test_create_user():
    user = create_user("张三")
    assert user.name == "张三"

def test_update_user():
    # Arrange 阶段自己创建数据
    user = create_user("张三")
    # Act
    updated = update_user(user.id, name="李四")
    # Assert
    assert updated.name == "李四"
```

**理由**：每个测试独立创建数据，执行顺序无关。任何测试都可以单独运行或并发运行，CI 中测试失败时问题定位准确。

---

### ❌ 反模式 2：Mock 了不该 Mock 的东西

```python
# 测试订单服务的折扣计算
def test_apply_discount():
    # ❌ Mock 了内部业务逻辑
    discount_calc = Mock(return_value=20.0)
    order_service = OrderService(discount_calc=discount_calc)
    
    result = order_service.apply_discount(order)
    assert result == 80.0  # 这个测试只验证了 Mock 的行为！
```

**问题**：真实的折扣计算逻辑从未被执行。如果 `DiscountCalculator` 有 bug，这个测试永远不会发现。表面覆盖率达到了，但核心逻辑没有测试。

### ✅ 正确做法：Mock 外部边界，测试真实逻辑

```python
def test_apply_discount_vip_gets_20_percent():
    # Arrange — 只 Mock 数据库
    db = Mock()
    db.get_user.return_value = User(role="vip")
    order_service = OrderService(db=db)
    order = Order(total=100.0)
    
    # Act — 真实的折扣计算
    result = order_service.apply_discount(order)
    
    # Assert — 验证真实计算结果
    assert result == 80.0  # 20% 折扣
```

**理由**：数据库是外部依赖需要 Mock，但折扣计算是业务核心逻辑，必须真实执行。测试验证的是"VIP 用户确实享受了 20% 折扣"这个行为，而非"Mock 返回了 20"。

---

### ❌ 反模式 3：只测 Happy Path

```python
def test_transfer_money_success():
    result = transfer("A", "B", 100)
    assert result.status == "success"

# 没有测试：A 余额不足、B 账户不存在、转账金额为负数、并发重复转账...
```

**问题**：生产环境 80% 的故障来自边界条件和异常路径，但测试只覆盖了正常情况。上线后有信心"正常情况没问题"，但对"出问题时系统怎么表现"毫无把握。

### ✅ 正确做法：覆盖正常 + 边界 + 异常

```python
def test_transfer_money_success():
    result = transfer("A", "B", 100)
    assert result.status == "success"

def test_transfer_insufficient_balance():
    with pytest.raises(InsufficientBalanceError):
        transfer("A", "B", 1_000_000)

def test_transfer_to_nonexistent_account():
    with pytest.raises(AccountNotFoundError):
        transfer("A", "GHOST", 100)

def test_transfer_zero_amount():
    with pytest.raises(InvalidAmountError):
        transfer("A", "B", 0)

def test_transfer_negative_amount():
    with pytest.raises(InvalidAmountError):
        transfer("A", "B", -100)
```

**理由**：每个异常路径一个测试，函数输入域被完整覆盖。重构时如果不小心让"零金额"通过了校验，对应的测试会立即失败。

---

## 四、示例

### 场景 1：从零开始写一个测试

**需求**：`split_bill(total, num_people)` 函数，计算 AA 制每人应付金额。

| | 反例 | 正例 |
|---|------|------|
| 测试 | 只写一个测试：`test_split_bill()` 验证 `split_bill(100, 2) == 50` | 写四个测试：整数均分、不能整除时向上取整、人数为 0 抛异常、金额为负抛异常 |
| 说明 | Happy path 通过就认为"测完了"，实际除法精度、非法输入都没覆盖 | 覆盖正常值、边界值、异常值，函数的行为被完整定义 |

### 场景 2：测试与 CI 的配合

**需求**：PR 合入前自动运行测试，不通过则阻止合入。

| | 反例 | 正例 |
|---|------|------|
| 流程 | CI 跑 15 分钟，开发者提交后干等；偶尔因为时间相关的测试随机失败（flaky test），大家学会"重跑就行了" | 单元测试 20 秒跑完，集成测试 2 分钟跑完，E2E 仅在 release 分支跑。flaky test 单独标记并优先修复，不允许"重跑通过就当无事发生" |
| 说明 | 慢 CI 让开发者放弃频繁提交，flaky test 让团队对测试失去信任 | 快速反馈让开发者愿意频繁跑测试；严格的 flaky test 处理保持测试可靠性 |

---

## 五、工具推荐

| 工具 | 用途 | 推荐度 |
|------|------|--------|
| pytest / Jest / JUnit | 测试框架 | 必须 |
| pytest-cov / Istanbul (nyc) | 覆盖率报告 | 推荐 |
| FactoryBoy / Faker | 测试数据生成 | 推荐 |
| pytest-mock / jest.mock | Mock 框架 | 推荐 |
| Selenium / Playwright | E2E 测试 | 可选 |
| Allure / JUnit XML | 测试报告聚合 | 可选 |

---

## 六、检查清单

- [ ] 单元/集成/E2E 三层测试比例是否合理（~70/20/10）？
- [ ] 测试是否遵循 AAA（Arrange-Act-Assert）模式？
- [ ] 测试命名是否描述了"方法_场景_期望"？
- [ ] 每个测试是否独立运行，不依赖执行顺序？
- [ ] 是否只 Mock 了外部边界，没有 Mock 内部模块？
- [ ] 是否覆盖了边界条件（空值/零值/极大值）？
- [ ] 是否覆盖了关键异常路径（超时/宕机/非法输入）？
- [ ] 是否有 flaky test（时过时不过的测试）？应立即修复
- [ ] 覆盖率是否达到当前阶段目标？
- [ ] CI 中测试是否全部通过？

---

## 更新记录

| 日期 | 版本 | 变更说明 |
|------|------|---------|
| 2026-05-26 | v1.0 | 按统一模板改造：新增核心原则（为什么）、反模式（3组）、完整场景示例、工具推荐、检查清单（10项） |
