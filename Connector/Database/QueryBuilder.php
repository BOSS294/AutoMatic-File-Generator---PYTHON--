<?php
declare(strict_types=1);

/**
 * NileAndSinai V2 - Safe Query Builder
 * Version: 2.0.0
 *
 * Adds strict SQL identifier validation while retaining prepared-value bindings.
 * Table/column/order identifiers must be controlled application identifiers;
 * user-controlled SQL identifiers are rejected.
 */

final class QueryBuilder
{
    private string $type = 'select';
    private string $table = '';
    private array $columns = ['*'];
    private array $wheres = [];
    private array $bindings = [];
    private array $orders = [];
    private ?int $limit = null;
    private ?int $offset = null;
    private array $insertData = [];
    private array $updateData = [];

    public static function table(string $table): self
    {
        $qb = new self();
        $qb->table = self::identifier($table);
        return $qb;
    }

    public function select(array $columns = ['*']): self
    {
        $this->type = 'select';
        $this->columns = array_map(
            static fn(string $column): string => self::selectIdentifier($column),
            $columns
        );
        return $this;
    }

    public function insert(array $data): self
    {
        if ($data === []) {
            throw new InvalidArgumentException('Insert data cannot be empty.');
        }

        $this->type = 'insert';
        $this->insertData = $this->normalizeDataIdentifiers($data, 'insert');
        return $this;
    }

    public function update(array $data): self
    {
        if ($data === []) {
            throw new InvalidArgumentException('Update data cannot be empty.');
        }

        $this->type = 'update';
        $this->updateData = $this->normalizeDataIdentifiers($data, 'update');
        return $this;
    }

    public function delete(): self
    {
        $this->type = 'delete';
        return $this;
    }

    public function where(string $column, mixed $value, string $operator = '='): self
    {
        $operator = strtoupper(trim($operator));

        $allowedOperators = [
            '=', '!=', '<>', '<', '>', '<=', '>=',
            'LIKE', 'NOT LIKE', 'IS', 'IS NOT',
        ];

        if (!in_array($operator, $allowedOperators, true)) {
            throw new InvalidArgumentException('Unsupported WHERE operator.');
        }

        $column = self::identifier($column);
        $placeholder = ':w' . count($this->bindings);

        $this->wheres[] = [$column, $operator, $placeholder];
        $this->bindings[$placeholder] = $value;

        return $this;
    }

    public function whereNull(string $column): self
    {
        $this->wheres[] = [self::identifier($column), 'IS', 'NULL'];
        return $this;
    }

    public function whereNotNull(string $column): self
    {
        $this->wheres[] = [self::identifier($column), 'IS NOT', 'NULL'];
        return $this;
    }

    public function orderBy(string $column, string $direction = 'ASC'): self
    {
        $direction = strtoupper(trim($direction));
        if (!in_array($direction, ['ASC', 'DESC'], true)) {
            throw new InvalidArgumentException('Unsupported ORDER BY direction.');
        }

        $this->orders[] = self::identifier($column) . ' ' . $direction;
        return $this;
    }

    public function limit(int $limit, ?int $offset = null): self
    {
        if ($limit < 0 || ($offset !== null && $offset < 0)) {
            throw new InvalidArgumentException('LIMIT/OFFSET must be non-negative.');
        }

        $this->limit = $limit;
        $this->offset = $offset;
        return $this;
    }

    public function toSql(): string
    {
        return match ($this->type) {
            'select' => $this->buildSelect(),
            'insert' => $this->buildInsert(),
            'update' => $this->buildUpdate(),
            'delete' => $this->buildDelete(),
            default => throw new RuntimeException('Unsupported query type.'),
        };
    }

    public function bindings(): array
    {
        return $this->bindings;
    }

    private function buildSelect(): string
    {
        $sql = 'SELECT ' . implode(', ', $this->columns)
            . ' FROM ' . $this->table;

        $sql .= $this->compileWhere();
        $sql .= $this->compileOrder();
        $sql .= $this->compileLimit();

        return $sql;
    }

    private function buildInsert(): string
    {
        $columns = array_keys($this->insertData);
        $placeholders = [];

        foreach ($columns as $column) {
            $placeholder = ':i_' . preg_replace('/[^A-Za-z0-9_]/', '_', $column);
            $placeholder .= '_' . count($placeholders);
            $placeholders[] = $placeholder;
            $this->bindings[$placeholder] = $this->insertData[$column];
        }

        return 'INSERT INTO ' . $this->table
            . ' (' . implode(', ', $columns) . ') VALUES ('
            . implode(', ', $placeholders) . ')';
    }

    private function buildUpdate(): string
    {
        $sets = [];

        foreach ($this->updateData as $column => $value) {
            $placeholder = ':u_' . preg_replace('/[^A-Za-z0-9_]/', '_', $column);
            $placeholder .= '_' . count($sets);
            $sets[] = $column . ' = ' . $placeholder;
            $this->bindings[$placeholder] = $value;
        }

        return 'UPDATE ' . $this->table
            . ' SET ' . implode(', ', $sets)
            . $this->compileWhere();
    }

    private function buildDelete(): string
    {
        return 'DELETE FROM ' . $this->table . $this->compileWhere();
    }

    private function compileWhere(): string
    {
        if ($this->wheres === []) {
            return '';
        }

        $parts = [];

        foreach ($this->wheres as [$column, $operator, $value]) {
            if (($operator === 'IS' || $operator === 'IS NOT')
                && ($value === 'NULL' || $value === 'NOT NULL')) {
                $parts[] = "{$column} {$operator} {$value}";
            } else {
                $parts[] = "{$column} {$operator} {$value}";
            }
        }

        return ' WHERE ' . implode(' AND ', $parts);
    }

    private function compileOrder(): string
    {
        return $this->orders === []
            ? ''
            : ' ORDER BY ' . implode(', ', $this->orders);
    }

    private function compileLimit(): string
    {
        if ($this->limit === null) {
            return '';
        }

        $sql = ' LIMIT ' . $this->limit;

        if ($this->offset !== null) {
            $sql .= ' OFFSET ' . $this->offset;
        }

        return $sql;
    }

    private static function identifier(string $value): string
    {
        $value = trim($value);

        /*
         * Supports normal MySQL-style qualified names:
         * users, users.id, schema.users, schema.users.id
         */
        if ($value === '' || !preg_match(
            '/^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$/',
            $value
        )) {
            throw new InvalidArgumentException('Invalid SQL identifier.');
        }

        return $value;
    }

    private static function selectIdentifier(string $value): string
    {
        $value = trim($value);

        if ($value === '*') {
            return '*';
        }

        /*
         * Deliberately allows only simple aliases:
         * column
         * table.column
         * column AS alias
         */
        if (preg_match(
            '/^([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)(?:\s+AS\s+([A-Za-z_][A-Za-z0-9_]*))?$/i',
            $value,
            $m
        )) {
            return isset($m[2]) && $m[2] !== ''
                ? $m[1] . ' AS ' . $m[2]
                : $m[1];
        }

        throw new InvalidArgumentException('Invalid SELECT identifier.');
    }

    private function normalizeDataIdentifiers(array $data, string $context): array
    {
        $result = [];

        foreach ($data as $column => $value) {
            if (!is_string($column)) {
                throw new InvalidArgumentException("{$context} column names must be strings.");
            }

            $result[self::identifier($column)] = $value;
        }

        return $result;
    }
}