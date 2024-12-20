<?php

namespace App\Http\Controllers;

use App\Models\Exam;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class ExamController extends Controller
{
    // Получение списка экзаменов пользователя
    public function index()
    {
        if (!auth()->check()) {
            return response()->json(['message' => 'Unauthenticated'], 401);
        }
        $user = Auth::user();
        $exams = $user->exams()->with('questions')->get();

        return response()->json($exams);
    }

    // Получение одного экзамена
    public function show(Exam $exam)
    {
        // Проверка, что экзамен принадлежит текущему пользователю
        if ($exam->user_id !== Auth::id()) {
            return response()->json(['error' => 'Доступ запрещён'], 403);
        }

        return response()->json($exam->load('questions'));
    }

    // Создание нового экзамена
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'date' => 'required|date',
        ]);

        $exam = Auth::user()->exams()->create($validated);

        return response()->json($exam, 201);
    }

    // Обновление экзамена
    public function update(Request $request, Exam $exam)
    {
        // Проверка, что экзамен принадлежит текущему пользователю
        if ($exam->user_id !== Auth::id()) {
            return response()->json(['error' => 'Доступ запрещён'], 403);
        }

        $validated = $request->validate([
            'name' => 'string|max:255',
            'date' => 'date',
        ]);

        $exam->update($validated);

        return response()->json($exam);
    }

    // Удаление экзамена
    public function destroy(Exam $exam)
    {
        // Проверка, что экзамен принадлежит текущему пользователю
        if ($exam->user_id !== Auth::id()) {
            return response()->json(['error' => 'Доступ запрещён'], 403);
        }

        $exam->delete();

        return response()->json(['message' => 'Экзамен удалён']);
    }
}