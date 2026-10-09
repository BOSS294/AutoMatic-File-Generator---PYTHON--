<?php
declare(strict_types=1);

final class ValidationException extends RuntimeException
{
    private array $errors;

    public function __construct(
        string $message = 'Validation failed.',
        array $errors = [],
        int $code = 422,
        ?Throwable $previous = null
    ) {
        $this->errors = $errors;
        parent::__construct($message, $code, $previous);
    }

    public function errors(): array
    {
        return $this->errors;
    }
}