# utils/async_processor.py - Fixed version with proper type handling

import asyncio
import logging
from typing import Optional, Any, Callable, Dict, List, Union, Awaitable
from datetime import datetime, timedelta  # Fix: Added timedelta import
import concurrent.futures
import threading
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskResult:
    """Container for task execution results"""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None

class AsyncProcessor:
    """Async processor for handling background tasks"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, TaskResult] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self._task_counter = 0
        self._lock = threading.Lock()
    
    def _generate_task_id(self, name: Optional[str] = None) -> str:
        """Generate a unique task ID with proper None handling"""
        with self._lock:
            self._task_counter += 1
            # Fix for line 29 error - handle None case properly
            if name is None or name.strip() == "":
                base_name = "task"
            else:
                base_name = str(name).strip()
            
            return f"{base_name}_{self._task_counter}_{int(datetime.now().timestamp())}"
    
    async def submit_task(
        self, 
        func: Callable, 
        *args, 
        name: Optional[str] = None, 
        timeout: Optional[float] = None,
        **kwargs
    ) -> str:
        """Submit a task for async execution"""
        try:
            task_id = self._generate_task_id(name)
            
            # Create task result entry
            task_result = TaskResult(
                task_id=task_id,
                status=TaskStatus.PENDING,
                start_time=datetime.now()
            )
            self.tasks[task_id] = task_result
            
            # Create and start the async task
            async_task = asyncio.create_task(
                self._execute_task(task_id, func, args, kwargs, timeout)
            )
            self.running_tasks[task_id] = async_task
            
            logger.info(f"Submitted task {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            raise
    
    async def _execute_task(
        self, 
        task_id: str, 
        func: Callable, 
        args: tuple, 
        kwargs: dict, 
        timeout: Optional[float] = None
    ) -> Any:
        """Execute a task with proper error handling"""
        task_result = self.tasks[task_id]
        task_result.status = TaskStatus.RUNNING
        
        try:
            # Run in executor for CPU-bound tasks
            if timeout:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        self.executor, func, *args, **kwargs
                    ),
                    timeout=timeout
                )
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor, func, *args, **kwargs
                )
            
            # Update task result
            task_result.status = TaskStatus.COMPLETED
            task_result.result = result
            task_result.end_time = datetime.now()
            
            if task_result.start_time:
                task_result.duration = (task_result.end_time - task_result.start_time).total_seconds()
            
            logger.info(f"Task {task_id} completed successfully")
            return result
            
        except asyncio.TimeoutError:
            task_result.status = TaskStatus.FAILED
            task_result.error = f"Task timed out after {timeout} seconds"
            task_result.end_time = datetime.now()
            logger.error(f"Task {task_id} timed out")
            raise
            
        except asyncio.CancelledError:
            task_result.status = TaskStatus.CANCELLED
            task_result.error = "Task was cancelled"
            task_result.end_time = datetime.now()
            logger.info(f"Task {task_id} was cancelled")
            raise
            
        except Exception as e:
            task_result.status = TaskStatus.FAILED
            task_result.error = str(e)
            task_result.end_time = datetime.now()
            logger.error(f"Task {task_id} failed: {e}")
            raise
            
        finally:
            # Clean up running task reference
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    async def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """Get the status of a specific task"""
        return self.tasks.get(task_id)
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> TaskResult:
        """Wait for a specific task to complete"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        if task_id in self.running_tasks:
            try:
                if timeout:
                    await asyncio.wait_for(self.running_tasks[task_id], timeout=timeout)
                else:
                    await self.running_tasks[task_id]
            except asyncio.TimeoutError:
                logger.warning(f"Timeout waiting for task {task_id}")
            except Exception as e:
                logger.error(f"Error waiting for task {task_id}: {e}")
        
        return self.tasks[task_id]
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.cancel()
            
            # Update task status
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.CANCELLED
                self.tasks[task_id].end_time = datetime.now()
            
            logger.info(f"Cancelled task {task_id}")
            return True
        
        logger.warning(f"Task {task_id} not found or not running")
        return False
    
    async def get_all_tasks(self) -> Dict[str, TaskResult]:
        """Get all task results"""
        return self.tasks.copy()
    
    async def cleanup_completed_tasks(self, max_age_hours: int = 24) -> int:
        """Clean up completed tasks older than specified hours"""
        # Fix for line 140 error - timedelta is now properly imported
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        tasks_to_remove = []
        for task_id, task_result in self.tasks.items():
            if (task_result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] 
                and task_result.end_time 
                and task_result.end_time < cutoff_time):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
        
        logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")
        return len(tasks_to_remove)
    
    async def get_running_tasks(self) -> List[str]:
        """Get list of currently running task IDs"""
        return list(self.running_tasks.keys())
    
    async def shutdown(self, wait: bool = True, timeout: Optional[float] = 30.0) -> None:
        """Shutdown the processor and clean up resources"""
        logger.info("Shutting down AsyncProcessor...")
        
        # Cancel all running tasks
        for task_id in list(self.running_tasks.keys()):
            await self.cancel_task(task_id)
        
        # Wait for tasks to complete if requested
        if wait and self.running_tasks:
            try:
                if timeout:
                    await asyncio.wait_for(
                        asyncio.gather(*self.running_tasks.values(), return_exceptions=True),
                        timeout=timeout
                    )
                else:
                    await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for tasks to complete during shutdown")
        
        # Shutdown executor
        self.executor.shutdown(wait=wait)
        logger.info("AsyncProcessor shutdown complete")


class BatchProcessor:
    """Process multiple tasks in batches"""
    
    def __init__(self, processor: AsyncProcessor, batch_size: int = 10):
        self.processor = processor
        self.batch_size = batch_size
    
    async def process_batch(
        self, 
        items: List[Any], 
        func: Callable,
        batch_name: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[TaskResult]:
        """Process items in batches"""
        results = []
        total_items = len(items)
        
        # Create batches
        for i in range(0, total_items, self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            
            # Process batch
            batch_tasks = []
            for j, item in enumerate(batch):
                task_name = f"{batch_name}_batch_{batch_num}_item_{j}" if batch_name else None
                task_id = await self.processor.submit_task(func, item, name=task_name)
                batch_tasks.append(task_id)
            
            # Wait for batch to complete
            batch_results = []
            for task_id in batch_tasks:
                result = await self.processor.wait_for_task(task_id)
                batch_results.append(result)
            
            results.extend(batch_results)
            
            # Call progress callback if provided
            if progress_callback:
                completed_items = min(i + self.batch_size, total_items)
                progress_callback(completed_items, total_items)
        
        return results


# Convenience functions
async def run_async_task(
    func: Callable, 
    *args, 
    name: Optional[str] = None,
    timeout: Optional[float] = None,
    **kwargs
) -> Any:
    """Run a single async task with automatic cleanup"""
    processor = AsyncProcessor(max_workers=1)
    
    try:
        task_id = await processor.submit_task(func, *args, name=name, timeout=timeout, **kwargs)
        result = await processor.wait_for_task(task_id)
        
        if result.status == TaskStatus.COMPLETED:
            return result.result
        else:
            raise Exception(f"Task failed: {result.error}")
    
    finally:
        await processor.shutdown()


async def run_parallel_tasks(
    tasks: List[tuple], 
    max_workers: int = 4,
    timeout: Optional[float] = None
) -> List[TaskResult]:
    """Run multiple tasks in parallel"""
    processor = AsyncProcessor(max_workers=max_workers)
    
    try:
        # Submit all tasks
        task_ids = []
        for i, task_def in enumerate(tasks):
            if len(task_def) >= 2:
                func, args = task_def[0], task_def[1:]
                task_id = await processor.submit_task(func, *args, name=f"parallel_task_{i}", timeout=timeout)
                task_ids.append(task_id)
        
        # Wait for all tasks
        results = []
        for task_id in task_ids:
            result = await processor.wait_for_task(task_id)
            results.append(result)
        
        return results
    
    finally:
        await processor.shutdown()


# Example usage for CSV processing
async def process_csv_async(
    csv_data: Any, 
    processing_func: Callable,
    chunk_size: int = 1000,
    max_workers: int = 4
) -> List[Any]:
    """Process CSV data asynchronously in chunks"""
    import pandas as pd
    
    if not isinstance(csv_data, pd.DataFrame):
        raise ValueError("csv_data must be a pandas DataFrame")
    
    # Split DataFrame into chunks
    chunks = [csv_data[i:i + chunk_size] for i in range(0, len(csv_data), chunk_size)]
    
    # Process chunks in parallel
    processor = AsyncProcessor(max_workers=max_workers)
    batch_processor = BatchProcessor(processor, batch_size=max_workers)
    
    try:
        results = await batch_processor.process_batch(
            chunks, 
            processing_func,
            batch_name="csv_processing"
        )
        
        # Combine results
        combined_results = []
        for result in results:
            if result.status == TaskStatus.COMPLETED and result.result is not None:
                combined_results.append(result.result)
            else:
                logger.warning(f"Chunk processing failed: {result.error}")
        
        return combined_results
    
    finally:
        await processor.shutdown()