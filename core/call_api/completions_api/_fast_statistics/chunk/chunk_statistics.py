import numpy as np
from typing import Generator
from .....request_log import RequestLog
from ..format import (
    format_title,
    format_timedelta,
    Chart
)
from .chunk_spawn_time import ChunkSpawnTime
from .queue_backlog import QueueBacklog

class ChunkStatistics:
    def __init__(
        self,
        name: str,
        request_log: RequestLog,
        raw_timestamps: list[int],
        raw_queue_backlogs: list[int] | None = None,
    ):
        self.name = name
        self.timestamps = np.array(raw_timestamps, dtype=np.int64)
        self.time_differences = np.diff(self.timestamps)
        self.non_zero_time_differences = self.time_differences[self.time_differences != 0]
        self.stream_processing_time = request_log.stream_processing_end_time.monotonic - request_log.stream_processing_start_time.monotonic
        self.raw_queue_backlogs = raw_queue_backlogs
        if self.raw_queue_backlogs is not None:
            self.queue_backlogs = np.array(self.raw_queue_backlogs, dtype=np.int64)

        self.chunk_spawn_time: ChunkSpawnTime | None = None
        self.queue_backlog: QueueBacklog | None = None

        if self.time_differences.size > 0 and self.non_zero_time_differences.size > 0:
            self.first_chunk_wait_time: np.int64 = self.timestamps[0] - request_log.stream_processing_start_time.monotonic
            self.chunk_spawn_time = ChunkSpawnTime(
                stream_processing_start_time = request_log.stream_processing_start_time,
                stream_processing_end_time = request_log.stream_processing_end_time,
                total_chunks = request_log.total_chunk,
                time_differences = self.time_differences,
                non_zero_time_differences = self.non_zero_time_differences
            )
            self.chunk_spawn_time_chart = Chart(
                title = f"{name} Chunk Times",
                data = self.time_differences,
            )
            if self.raw_queue_backlogs is not None:
                self.queue_backlog = QueueBacklog(
                    queue_backlogs = self.queue_backlogs
                )

                self.queue_backlog_chart = Chart(
                    title = f"{name} Queue Backlog",
                    data = self.queue_backlogs,
                )
    
    def format_statistics(
        self,
        title_width: int = 50,
        chart_width: int = 50,
        chart_height: int = 10,
        dividing_line_char: str = "=",
        step_char: str = "\n",
    ) -> str:
        buffer: list[str] = []
        
        buffer.extend(
            self.format_statistics_stream(
                title_width = title_width,
                chart_width = chart_width,
                chart_height = chart_height,
                dividing_line_char = dividing_line_char,
            )
        )
        return step_char.join(buffer)

    def format_statistics_stream(
        self,
        title_width: int = 50,
        chart_width: int = 50,
        chart_height: int = 10,
        dividing_line_char: str = "=",
    ) -> Generator[str, None, None]:
        if title_width < len(self.name) + 2:
            raise ValueError("title_width must be at least as long as the name")

        title = f"{self.name} Chunk Statistics"
        if self.chunk_spawn_time is not None:

            yield format_title(
                title = title,
                dividing = dividing_line_char,
                title_width = title_width
            )

            yield from self.chunk_spawn_time_chart.draw_lines(
                width = chart_width,
                height = chart_height,
            )
            yield f"{self.name} Chunk Rate: {self.chunk_spawn_time.chunk_generation_rate:.2f} Chunks/s"
            yield f"{self.name} First Chunk Wait Time: {format_timedelta(int(self.first_chunk_wait_time))}"
            yield f"{self.name} Chunk Average Time: {format_timedelta(self.chunk_spawn_time.ave_chunk_spawn_time)}"
            yield f"{self.name} Chunk Max Time: {format_timedelta(self.chunk_spawn_time.max_chunk_spawn_time)}"
            yield f"{self.name} Chunk Min Time: {format_timedelta(self.chunk_spawn_time.min_chunk_spawn_time)}"
            yield f"{self.name} Chunk Time CV: {self.chunk_spawn_time.chunk_stability_cv:.2%}"
            yield f"{self.name} Chunk Time Range: {format_timedelta(self.chunk_spawn_time.chunk_spawn_time_range)}"
            yield f"{self.name} Chunk Time Median: {format_timedelta(self.chunk_spawn_time.chunk_median_time)}"
            yield f"{self.name} Chunk Time STD: {format_timedelta(self.chunk_spawn_time.chunk_spawn_time_std)}"
            yield f"{self.name} Chunk Time MAD: {format_timedelta(self.chunk_spawn_time.chunk_spawn_time_mad)}"
            yield f"{self.name} Chunk Time Relative MAD: {self.chunk_spawn_time.chunk_spawn_time_relative_mad:.2%}"
            yield f"{self.name} Chunk Time IQR: {format_timedelta(self.chunk_spawn_time.chunk_spawn_time_iqr)}"
            yield f"{self.name} Chunk Time IDR: {format_timedelta(self.chunk_spawn_time.chunk_spawn_time_idr)}"
            yield f"{self.name} Chunk P01 Time: {format_timedelta(self.chunk_spawn_time.chunk_spawn_time_p01)}"
            yield f"{self.name} Chunk P50 Time: {format_timedelta(self.chunk_spawn_time.chunk_spawn_time_p50)}"
            yield f"{self.name} Chunk P75 Time: {format_timedelta(self.chunk_spawn_time.chunk_spawn_time_p75)}"
            yield f"{self.name} Chunk P90 Time: {format_timedelta(self.chunk_spawn_time.chunk_spawn_time_p90)}"
            yield f"{self.name} Chunk P95 Time: {format_timedelta(self.chunk_spawn_time.chunk_spawn_time_p95)}"
            yield f"{self.name} Chunk P99 Time: {format_timedelta(self.chunk_spawn_time.chunk_spawn_time_p99)}"
            yield f"{self.name} Chunk P99 - P50 Time: {format_timedelta(self.chunk_spawn_time.chunk_spawn_time_p99 - self.chunk_spawn_time.chunk_spawn_time_p50)}"
            yield f"{self.name} Chunk Time Skewness: {self.chunk_spawn_time.skewness:.2%}"
            yield f"{self.name} Chunk Time Kurtosis: {self.chunk_spawn_time.kurtosis:.2%}"
            yield f"{self.name} Chunk Time Entropy: {self.chunk_spawn_time.entropy:.2%}"

            if self.queue_backlog is not None:

                yield from self.queue_backlog_chart.draw_lines(
                    width = chart_width,
                    height = chart_height,
                )
                yield f"{self.name} Max Queue Backlog: {self.queue_backlog.max_queue_backlog}"
                yield f"{self.name} Min Queue Backlog: {self.queue_backlog.min_queue_backlog}"
                yield f"{self.name} Avg Queue Backlog: {self.queue_backlog.avg_queue_backlog:.2f}"
                yield f"{self.name} Queue Backlog CV: {self.queue_backlog.queue_backlog_cv:.2%}"
                yield f"{self.name} Queue Backlog Range: {self.queue_backlog.queue_backlog_range}"
                yield f"{self.name} Queue Backlog Median: {self.queue_backlog.median_queue_backlog}"
                yield f"{self.name} Queue Backlog STD: {self.queue_backlog.queue_backlog_std:.2f}"
                yield f"{self.name} Queue Backlog MAD: {self.queue_backlog.queue_backlog_mad:.2f}"
                yield f"{self.name} Queue Backlog Relative MAD: {self.queue_backlog.queue_backlog_relative_mad:.2%}"
                yield f"{self.name} Queue Backlog IQR: {self.queue_backlog.queue_backlog_iqr}"
                yield f"{self.name} Queue Backlog IDR: {self.queue_backlog.queue_backlog_idr}"
                yield f"{self.name} Queue Backlog P01: {self.queue_backlog.queue_backlog_p01:.2f}"
                yield f"{self.name} Queue Backlog P50: {self.queue_backlog.queue_backlog_p50:.2f}"
                yield f"{self.name} Queue Backlog P75: {self.queue_backlog.queue_backlog_p75:.2f}"
                yield f"{self.name} Queue Backlog P90: {self.queue_backlog.queue_backlog_p90:.2f}"
                yield f"{self.name} Queue Backlog P95: {self.queue_backlog.queue_backlog_p95:.2f}"
                yield f"{self.name} Queue Backlog P99: {self.queue_backlog.queue_backlog_p99:.2f}"
                yield f"{self.name} Queue Backlog P99 - P50: {self.queue_backlog.queue_backlog_p99 - self.queue_backlog.queue_backlog_p50:.2f}"
                yield f"{self.name} Queue Backlog Skewness: {self.queue_backlog.queue_backlog_skewness:.2%}"
                yield f"{self.name} Queue Backlog Kurtosis: {self.queue_backlog.queue_backlog_kurtosis:.2%}"
                yield f"{self.name} Queue Backlog Entropy: {self.queue_backlog.queue_backlog_entropy:.2%}"