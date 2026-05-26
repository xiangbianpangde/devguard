"""表现层 — 订单控制器。

规则：接收 HTTP 请求，参数校验，调用应用层，返回响应。
不包含业务逻辑，不直接操作数据库。
"""
from ..application.order_service import OrderService


class OrderController:
    """订单控制器 — 表现层入口。

    为什么这么薄：
    - 业务规则在领域层（DiscountCalculator）
    - 流程编排在应用层（OrderService）
    - 数据库操作在基础设施层（PostgresOrderRepository）
    - 控制器只负责 HTTP ↔ 应用层的协议转换
    """

    def __init__(self, service: OrderService):
        self.service = service

    def create_order(self, request_body: dict) -> dict:
        """POST /api/orders — 创建订单。

        职责：校验输入 → 调用应用层 → 返回统一响应。
        """
        # 1. 参数校验（表现层的职责）
        required = ["order_id", "user_id", "product_id", "quantity", "unit_price"]
        for field in required:
            if field not in request_body:
                return {"code": 40001, "message": f"缺少必填字段: {field}", "data": None}

        if request_body["quantity"] <= 0:
            return {"code": 40002, "message": "数量必须大于 0", "data": None}

        # 2. 调用应用层（表现层不关心内部如何计算折扣和持久化）
        try:
            order = self.service.place_order(
                order_id=request_body["order_id"],
                user_id=request_body["user_id"],
                product_id=request_body["product_id"],
                quantity=request_body["quantity"],
                unit_price=request_body["unit_price"],
                is_vip=request_body.get("is_vip", False),
            )
        except Exception as e:
            return {"code": 50000, "message": f"创建订单失败: {e}", "data": None}

        # 3. 统一响应格式
        return {
            "code": 0,
            "message": "ok",
            "data": {
                "order_id": order.order_id,
                "status": order.status.value,
                "total": order.total,            # 原价
                "final_total": order.final_total,  # 折后应付
            },
        }
