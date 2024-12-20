<?php

namespace App\Services;

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

class RabbitMQService
{
    protected $connection;
    protected $channel;

    public function __construct()
    {
        // Параметры подключения
        $host = env('RABBITMQ_HOST', 'localhost');
        $port = env('RABBITMQ_PORT', 5672);
        $user = env('RABBITMQ_USER', 'guest');
        $pass = env('RABBITMQ_PASS', 'guest');

        $this->connection = new AMQPStreamConnection($host, $port, $user, $pass);
        $this->channel = $this->connection->channel();
    }

    public function createQueues()
    {
        // Создание очередей
        $this->channel->queue_declare('question_requests', false, true, false, false);
        $this->channel->queue_declare('question_responses', false, true, false, false);
        echo "Очереди успешно созданы!\n";
    }

    public function publishMessage(string $queue, string $message)
    {
        // Отправка сообщения в очередь
        $this->channel->queue_declare($queue, false, true, false, false);
        $msg = new AMQPMessage($message, ['delivery_mode' => 2]); // Устойчивое сообщение
        $this->channel->basic_publish($msg, '', $queue);
        echo "Сообщение отправлено в очередь: $queue\n";
    }

    public function consumeMessages(string $queue, callable $callback)
    {
        // Убедимся, что очередь существует
        $this->channel->queue_declare($queue, false, true, false, false);

        // Подписка на очередь
        $this->channel->basic_consume(
            $queue,          // Имя очереди
            '',              // Тег потребителя
            false,           // Нет автоматического согласования
            true,            // Автоматическое подтверждение
            false,           // Не эксклюзивно
            false,           // Не ожидать
            $callback        // Колбэк-функция для обработки сообщений
        );

        // Цикл обработки сообщений
        echo "Ожидание сообщений в очереди: $queue\n";
        while (true) {
            $this->channel->wait(); // Ожидание сообщений
        }
    }



    public function __destruct()
    {
        $this->channel->close();
        $this->connection->close();
    }
}