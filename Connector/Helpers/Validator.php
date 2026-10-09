<?php
declare(strict_types=1);

final class Validator
{
    public static function required(mixed $value): bool
    {
        return !($value === null || $value === '' || (is_array($value) && $value === []));
    }

    public static function email(string $value): bool
    {
        return filter_var($value, FILTER_VALIDATE_EMAIL) !== false;
    }

    public static function integer(mixed $value): bool
    {
        return filter_var($value, FILTER_VALIDATE_INT) !== false;
    }

    public static function boolean(mixed $value): bool
    {
        return filter_var($value, FILTER_VALIDATE_BOOL, FILTER_NULL_ON_FAILURE) !== null;
    }

    public static function uuid(string $value): bool
    {
        return (bool) preg_match('/^[0-9a-fA-F-]{36}$/', $value);
    }

    public static function in(mixed $value, array $allowed): bool
    {
        return in_array($value, $allowed, true);
    }
}
