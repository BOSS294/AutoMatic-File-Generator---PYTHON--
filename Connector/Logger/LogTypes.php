<?php
declare(strict_types=1);

final class LogTypes
{
    public const INFO = 'info';
    public const SUCCESS = 'success';
    public const WARNING = 'warning';
    public const BLOCKED = 'blocked';
    public const ERROR = 'error';
    public const CRITICAL = 'critical';

    public const SOURCE_PHP = 'php';
    public const SOURCE_JS = 'js';
    public const SOURCE_API = 'api';
    public const SOURCE_SYSTEM = 'system';
}
