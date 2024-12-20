<?php

namespace App\Http\Controllers;

use App\Models\Exam;
use App\Models\Question;
use Illuminate\Http\Request;
use PhpOffice\PhpSpreadsheet\IOFactory;
use Illuminate\Support\Facades\Validator;
use Log;

class QuestionImportController extends Controller
{
    public function import(Request $request, Exam $exam)
{
    // Проверка файла
    $validator = Validator::make($request->all(), [
        'file' => 'required|file|mimes:xlsx,xls',
    ]);

    if ($validator->fails()) {
        return response()->json(['errors' => $validator->errors()], 422);
    }

    Question::where('exam_id', $exam->id)->delete();

    // Создаем директорию, если она не существует
    $directory = storage_path('app/temp');
    if (!is_dir($directory)) {
        mkdir($directory, 0775, true);
    }

    // Загрузка файла
    $filePath = $request->file('file')->store('temp', 'public'); // Сохраняет в storage/app/public

    $fullPath = storage_path('app/public/' . $filePath);


    // Проверяем, существует ли файл
    if (!file_exists($fullPath)) {
        return response()->json(['error' => 'Файл не существует по пути: ' . $fullPath], 400);
    }

    // Чтение данных из файла Excel
    try {
        $spreadsheet = IOFactory::load($fullPath);
        $sheetData = $spreadsheet->getActiveSheet()->toArray(null, true, true, true);

        foreach ($sheetData as $index => $row) {
            if ($index === 1) {
                // Пропускаем заголовок таблицы
                continue;
            }



            $question = trim($row['A']);
            $answer = trim($row['B']);

            if (empty($question) || empty($answer)) {
                return response()->json([
                    'error' => "Ошибка в строке {$index}: вопрос или ответ пусты.",
                ], 400);
            }

            if (empty($question) || empty($answer)) {
                return response()->json([
                    'error' => "Ошибка в строке {$index}: вопрос или ответ пусты.",
                ], 400);
            }

            // Сохранение вопроса в базе данных
            Question::create([
                'exam_id' => $exam->id,
                'question' => $question,
                'answer' => $answer,
                'is_public' => false, // По умолчанию приватный
            ]);
        }
        if (file_exists($fullPath)) {
            unlink($fullPath);
        }

        return response()->json(['message' => 'Вопросы успешно добавлены.']);

    } catch (\Exception $e) {
        if (file_exists($fullPath)) {
            unlink($fullPath);
        }
        return response()->json(['error' => 'Ошибка при обработке файла: ' . $e->getMessage()], 500);
    }
}

}