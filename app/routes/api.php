<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\QuestionImportController;
use App\Http\Controllers\ExamController;

Route::get('/hello', function () {
    return response()->json(['message' => 'Hello, World!']);
});



// Группа маршрутов для аутентификации с префиксом 'auth' и именем маршрута
Route::prefix('auth')->name('auth.')->group(function () {
    Route::middleware('throttle:5,1')->group(function () {
        Route::post('register', [App\Http\Controllers\AuthController::class, 'register'])->name('register');
        Route::post('login', [App\Http\Controllers\AuthController::class, 'login'])->name('login');
    });

    Route::middleware('auth:sanctum')->group(function () {
        Route::post('logout', [App\Http\Controllers\AuthController::class, 'logout'])->name('logout');
    });
});

// Группа маршрутов с аутентификацией для работы с экзаменами
Route::middleware('auth:sanctum')->group(function () {
    Route::post('/exams/{exam}/import-questions', [QuestionImportController::class, 'import']); // Импорт вопросов из файла
    Route::get('exams', [ExamController::class, 'index'])->name('exams.index'); // Получение списка экзаменов
    Route::get('exams/{exam}', [ExamController::class, 'show'])->name('exams.show'); // Получение одного экзамена
    Route::post('exams', [ExamController::class, 'store'])->name('exams.store'); // Создание экзамена
    Route::put('exams/{exam}', [ExamController::class, 'update'])->name('exams.update'); // Обновление экзамена
    Route::delete('exams/{exam}', [ExamController::class, 'destroy'])->name('exams.destroy'); // Удаление экзамена

    
});