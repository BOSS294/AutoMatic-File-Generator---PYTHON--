<?php
declare(strict_types=1);

final class AuthorizationException extends RuntimeException
{
    public function __construct(
        string $message = 'Access denied.',
        int $code = 403,
        ?Throwable $previous = null
    ) {
        parent::__construct($message, $code, $previous);
    }
}