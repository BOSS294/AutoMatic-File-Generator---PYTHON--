<?php
declare(strict_types=1);

final class SecurityException extends RuntimeException
{
    public function __construct(
        string $message = 'Security validation failed.',
        int $code = 403,
        ?Throwable $previous = null
    ) {
        parent::__construct($message, $code, $previous);
    }
}