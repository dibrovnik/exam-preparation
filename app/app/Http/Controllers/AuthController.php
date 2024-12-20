<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;

class AuthController extends Controller
{
    public function register(Request $request): JsonResponse
    {
        $data = $request->validate([
            'name'      => 'required|string',
            'email'     => 'required|string|email|unique:users,email',
            'password'  => 'required|string|min:8|confirmed|regex:/[a-z]/|regex:/[A-Z]/|regex:/[0-9]/',
        ]);

        $user = User::create([
            'name'      => $data['name'],
            'email'     => $data['email'],
            'password'  => Hash::make($data['password'])
        ]);

        $token = $user->createToken('user-token')->plainTextToken;

        $response = [
            'user'  => $user->makeHidden(['password', 'remember_token']),
            'token' => $token
        ];

        return response()->json($response, 201);
    }

    public function login(Request $request): JsonResponse
    {
        $request->validate([
            'email'     => 'required|string|email',
            'password'  => 'required|string|min:8'
        ]);

        $user = User::where('email', $request->email)->first();

        if (!$user || !Hash::check($request->password, $user->password)) {
            return response()->json([
                'message' => 'These credentials do not match our records.'
            ], 401);
        }

        $token = $user->createToken('user-token')->plainTextToken;

        $response = [
            'user'  => $user->makeHidden(['password', 'remember_token']),
            'token' => $token
        ];

        return response()->json($response, 200);
    }

    public function logout()
    {
        Auth::user()->tokens->each(function ($token) {
            $token->forceDelete();
        });

        return response()->json([
            'message' => 'Logged out successfully',
        ], 200);
    }
}