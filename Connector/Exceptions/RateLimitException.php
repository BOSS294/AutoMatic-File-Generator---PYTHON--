<?php
declare(strict_types=1);

final class RateLimitException extends RuntimeException
{
    private array $meta;

    public function __construct(
        string $message = 'Too many requests.',
        array $meta = [],
        int $code = 429,
        ?Throwable $previous = null
    ) {
        $this->meta = $meta;
        parent::__construct($message, $code, $previous);
    }

    public function meta(): array
    {
        return $this->meta;
    }
}