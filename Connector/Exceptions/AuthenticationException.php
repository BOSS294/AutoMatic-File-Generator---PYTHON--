<?php
declare(strict_types=1);

final class AuthenticationException extends RuntimeException
{
    public function __construct(
        string $message = 'Authentication required.',
        int $code = 401,
        ?Throwable $previous = null
    ) {
        parent::__construct($message, $code, $previous);
    }
}