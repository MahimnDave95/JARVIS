package com.yourname.jarvismobile

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException

class CommandSender {
    private val TAG = "CommandSender"
    
    sealed class Result {
        data class Success(val message: String) : Result()
        data class Error(val message: String) : Result()
    }
    
    suspend fun sendCommand(command: String): Result = withContext(Dispatchers.IO) {
        try {
            val response = ApiClient.getApiService().sendCommand(CommandRequest(command))
            
            if (response.success) {
                Result.Success(response.message)
            } else {
                Result.Error(response.message)
            }
        } catch (e: IOException) {
            Log.e(TAG, "Network error", e)
            Result.Error("Can't reach PC. Check connection. 😅")
        } catch (e: Exception) {
            Log.e(TAG, "Error sending command", e)
            Result.Error("Something went wrong: ${e.message}")
        }
    }
    
    suspend fun sendTypeText(text: String): Result = withContext(Dispatchers.IO) {
        try {
            val response = ApiClient.getApiService().sendTypeCommand(TypeRequest(text))
            
            if (response.success) {
                Result.Success("Typed ${text.length} chars! ⌨️")
            } else {
                Result.Error(response.message)
            }
        } catch (e: IOException) {
            Log.e(TAG, "Network error", e)
            Result.Error("Can't reach PC. Check connection. 😅")
        } catch (e: Exception) {
            Log.e(TAG, "Error sending type command", e)
            Result.Error("Failed to type: ${e.message}")
        }
    }
    
    suspend fun checkStatus(): Boolean = withContext(Dispatchers.IO) {
        try {
            val response = ApiClient.getApiService().getStatus()
            response.status == "online"
        } catch (e: Exception) {
            false
        }
    }
}