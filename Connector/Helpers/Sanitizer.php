<?php
declare(strict_types=1);

final class Sanitizer
{
    public static function text(?string $value): string
    {
        $value = trim((string) $value);
        $value = strip_tags($value);
        return preg_replace('/\s+/', ' ', $value) ?? '';
    }

    public static function array(array $items): array
    {
        $clean = [];
        foreach ($items as $key => $value) {
            $clean[$key] = is_string($value) ? self::text($value) : $value;
        }
        return $clean;
    }

    public static function email(?string $value): string
    {
        return strtolower(self::text($value));
    }

    public static function filename(?string $value): string
    {
        $value = self::text($value);
        $value = preg_replace('/[^A-Za-z0-9._-]/', '_', $value) ?? '';
        return trim($value, '_');
    }
}
