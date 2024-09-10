import typing as ty
from types import TracebackType
import io


class BinaryIOWindow(ty.BinaryIO):
    """Presents a window onto an underlying BinaryIO object in a duck-typable
    subclass, so functions that take a stream object can be presented a partial view
    onto a file-stream.

    Parameters
    ----------
    binary_io: ty.BinaryIO
        the base stream to be windowed
    start: int
        start of the window, if negative then intepreted as being from the end of the stream
    end: int
        end of the window, if negative then intepreted as being from the end of the stream
    """

    wrapped_io: ty.BinaryIO
    start: int
    end: int

    def __init__(self, binary_io: ty.BinaryIO, start: int, end: int):
        if binary_io.seekable() is False:
            binary_io = io.BytesIO(binary_io.read())
        self.wrapped_io = binary_io
        self.wrapped_io.seek(0, io.SEEK_END)
        file_size = self.wrapped_io.tell()
        self.start = start if start >= 0 else file_size + start
        self.end = end if end >= 0 else file_size + end
        self.size = self.end - self.start
        self.wrapped_io.seek(self.start)

    def read(self, size: ty.Optional[int] = -1) -> bytes:
        current_pos = self.tell()
        if current_pos >= self.size:
            return b""
        if size is None or size < 0 or (current_pos + size) > self.size:
            size = self.size - current_pos
        return self.wrapped_io.read(size)

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            ref = self.start
        elif whence == io.SEEK_CUR:
            ref = self.wrapped_io.tell()
        elif whence == io.SEEK_END:
            ref = self.end
        else:
            raise ValueError(
                f"Invalid value for 'whence' {whence}, should be 0, 1, or 2 "
                "(io.SEEK_SET, io.SEEK_CUR, io.SEEK_END)"
            )
        return self.wrapped_io.seek(ref + offset)

    def tell(self) -> int:
        return self.wrapped_io.tell() - self.start

    def __iter__(self) -> ty.Iterator[bytes]:
        return self.wrapped_io.__iter__()

    def __next__(self) -> bytes:
        return self.wrapped_io.__next__()

    @property
    def mode(self) -> str:
        return self.wrapped_io.mode

    @property
    def name(self) -> str:
        return self.wrapped_io.name

    def close(self) -> None:
        self.wrapped_io.close()

    @property
    def closed(self) -> bool:
        return self.wrapped_io.closed

    def fileno(self) -> int:
        return self.wrapped_io.fileno()

    def flush(self) -> None:
        self.wrapped_io.flush()

    def isatty(self) -> bool:
        return self.wrapped_io.isatty()

    def readable(self) -> bool:
        return self.wrapped_io.readable()

    def readline(self, limit: int = -1) -> bytes:
        return self.wrapped_io.readline()

    def readlines(self, hint: int = -1) -> ty.List[bytes]:
        return self.wrapped_io.readlines(hint)

    def seekable(self) -> bool:
        assert self.wrapped_io.seekable()
        return True

    def truncate(self, size: ty.Optional[int] = None) -> int:
        raise NotImplementedError

    def writable(self) -> bool:
        return False

    def write(self, s: bytes) -> int:  # type: ignore[override]
        raise NotImplementedError

    def writelines(self, lines: ty.Iterable[bytes]) -> None:  # type: ignore[override]
        raise NotImplementedError

    def __enter__(self) -> ty.BinaryIO:
        return self.wrapped_io.__enter__()

    def __exit__(
        self,
        type: ty.Optional[ty.Type[BaseException]],
        value: ty.Optional[BaseException],
        traceback: ty.Optional[TracebackType],
    ) -> None:
        return self.wrapped_io.__exit__(type, value, traceback)
