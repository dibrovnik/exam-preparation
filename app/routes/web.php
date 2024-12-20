<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\DB;

Route::get('/', function () {
    return view('welcome');
});

Route::get('/test-db', function () {
    try {
        DB::connection()->getPdo();
        return "Подключение успешно!";
    } catch (\Exception $e) {
        return "Ошибка подключения: " . $e->getMessage();
    }
});