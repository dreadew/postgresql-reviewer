# IO_AND_BUFFER_USAGE

description: Анализ использования shared buffers и дискового IO.
severity_default: medium
bad_example: |
EXPLAIN (ANALYZE, BUFFERS) SELECT \* FROM large_table;
-- Buffers: shared hit=100 read=10000, I/O read time: 500ms
good_example: |
EXPLAIN (ANALYZE, BUFFERS) SELECT \* FROM large_table WHERE indexed_col = 'value';
-- Buffers: shared hit=9500 read=100
notes: Высокий read (> 50% от total) указывает на недостаток индексов или кэширования.
