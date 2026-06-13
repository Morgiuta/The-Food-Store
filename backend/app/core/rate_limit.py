from collections import deque
from time import monotonic

from fastapi import HTTPException, Request, status


class FixedWindowFailureRateLimiter:
    def __init__(self, max_failures: int, window_seconds: int) -> None:
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self._failures: dict[str, deque[float]] = {}

    def _prune(self, key: str, now: float) -> deque[float]:
        failures = self._failures.setdefault(key, deque())
        cutoff = now - self.window_seconds
        while failures and failures[0] <= cutoff:
            failures.popleft()
        if not failures:
            self._failures.pop(key, None)
            failures = self._failures.setdefault(key, deque())
        return failures

    def retry_after(self, key: str) -> int:
        now = monotonic()
        failures = self._prune(key, now)
        if len(failures) < self.max_failures:
            return 0
        return max(1, int(self.window_seconds - (now - failures[0])))

    def assert_allowed(self, key: str) -> None:
        retry_after = self.retry_after(key)
        if retry_after <= 0:
            return
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Intente nuevamente mas tarde.",
            headers={"Retry-After": str(retry_after)},
        )

    def record_failure(self, key: str) -> None:
        failures = self._prune(key, monotonic())
        failures.append(monotonic())

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)


auth_failure_rate_limiter = FixedWindowFailureRateLimiter(
    max_failures=5,
    window_seconds=15 * 60,
)


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"
