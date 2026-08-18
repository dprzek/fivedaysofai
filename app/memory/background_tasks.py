import asyncio
import concurrent.futures
from typing import Any, Callable, Coroutine, Dict, List, Optional
from app.observability.tracer import tracer


class BackgroundMemoryWorker:
    """Asynchronous background task runner for non-blocking memory operations.
    
    Executes long-running CRM synchronization, memory consolidation, and analytics
    in the background without blocking conversational LLM response generation.
    """

    def __init__(self, max_workers: int = 4):
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._active_tasks: List[asyncio.Task] = []

    def run_coroutine_background(self, coro: Coroutine[Any, Any, Any], task_name: str = "background_task") -> asyncio.Task:
        """Schedules an asyncio coroutine in the background event loop."""
        tracer.info("background_task_scheduled", f"Scheduling async task: {task_name}", task_name=task_name)
        
        async def _wrapper():
            with tracer.trace_span(f"bg_task_{task_name}"):
                try:
                    await coro
                    tracer.info("background_task_completed", f"Completed async task: {task_name}", task_name=task_name)
                except Exception as e:
                    tracer.error("background_task_failed", f"Background task {task_name} failed: {str(e)}", task_name=task_name, error=str(e))

        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(_wrapper())
            self._active_tasks.append(task)
            return task
        except RuntimeError:
            # If no running event loop in current thread, run synchronously or via asyncio.run
            asyncio.run(_wrapper())
            return None

    def run_in_thread(self, fn: Callable[..., Any], *args: Any, task_name: str = "thread_task", **kwargs: Any) -> concurrent.futures.Future:
        """Executes a synchronous function in a separate thread pool."""
        tracer.info("thread_task_scheduled", f"Submitting thread task: {task_name}", task_name=task_name)
        
        def _thread_wrapper():
            with tracer.trace_span(f"thread_{task_name}"):
                try:
                    res = fn(*args, **kwargs)
                    tracer.info("thread_task_completed", f"Completed thread task: {task_name}", task_name=task_name)
                    return res
                except Exception as e:
                    tracer.error("thread_task_failed", f"Thread task {task_name} failed: {str(e)}", task_name=task_name, error=str(e))
                    raise

        return self._executor.submit(_thread_wrapper)

    def enqueue_compaction(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> concurrent.futures.Future:
        """Convenience method to schedule a memory compaction operation in background."""
        return self.run_in_thread(fn, *args, task_name="memory_compaction", **kwargs)


background_worker = BackgroundMemoryWorker()

