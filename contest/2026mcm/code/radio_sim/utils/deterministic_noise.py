"""用于可复现本地仿真的稳定键控测量误差。"""

from __future__ import annotations

import hashlib
import struct

from radio_sim.domain.models import Position


def measurement_error_deg(seed: int, channel: int, position: Position) -> float:
    """将（种子、信道、精确数值坐标）确定性映射到 [-1, 1]。

    在允许区间内采用均匀映射属于仿真假设。稳定哈希只是一种实现机制，
    用于满足官方关于同一地点重复测量误差保持不变的要求。
    """
    payload = bytearray()
    payload.extend(str(int(seed)).encode("ascii"))
    payload.extend(b"|")
    payload.extend(str(int(channel)).encode("ascii"))
    payload.extend(b"|")
    payload.extend(struct.pack("!d", position.x))
    payload.extend(struct.pack("!d", position.y))
    digest = hashlib.sha256(payload).digest()
    integer = int.from_bytes(digest[:8], byteorder="big", signed=False)
    unit = integer / ((1 << 64) - 1)
    return 2.0 * unit - 1.0
