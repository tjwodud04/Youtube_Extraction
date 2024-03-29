from typing import Callable, Generator, TypeVar

T = TypeVar("T")

def get_batches(elements: list[T], chunk_size: int) -> Generator[list[T], None, None]:
    for i in range(0, len(elements), chunk_size):
        yield elements[i:i + chunk_size]

def resize_chunk(chunk: list[T], target_length: int, defaultSupplier: Callable[[int], T]) -> list[T]:
     # Truncate or pad the translation to match the expected line count
    if len(chunk) > target_length:
        return chunk[:target_length]
    else:
        return chunk + [ defaultSupplier(index) for index in range(len(chunk) + 1, target_length + 1) ]

if __name__ == '__main__':
    elements = [1, 2, 3, 4, 5, 6, 7, 8]

    for batch in get_batches(elements, 3):
        print(batch)

    resized = resize_chunk([1, 2, 3], 5, lambda index: index)
    print(resized)

    resized = resize_chunk([1, 2, 3, 4, 5], 3, lambda index: index)
    print(resized)