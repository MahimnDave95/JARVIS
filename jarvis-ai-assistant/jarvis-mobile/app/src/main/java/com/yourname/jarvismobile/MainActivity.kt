package com.yourname.jarvismobile

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognizerIntent
import android.widget.Button
import android.widget.EditText
import android.widget.ImageButton
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    
    private lateinit var commandInput: EditText
    private lateinit var sendButton: Button
    private lateinit var micButton: ImageButton
    private lateinit var modeSwitch: Switch
    private lateinit var statusText: TextView
    private lateinit var settingsButton: ImageButton
    
    private val commandSender = CommandSender()
    private var isTypeMode = false // false = Control PC, true = Type on PC
    
    private val SPEECH_REQUEST_CODE = 100
    private val PERMISSION_REQUEST_CODE = 101
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initViews()
        setupListeners()
        checkPermissions()
        loadSettings()
    }
    
    private fun initViews() {
        commandInput = findViewById(R.id.commandInput)
        sendButton = findViewById(R.id.sendButton)
        micButton = findViewById(R.id.micButton)
        modeSwitch = findViewById(R.id.modeSwitch)
        statusText = findViewById(R.id.statusText)
        settingsButton = findViewById(R.id.settingsButton)
    }
    
    private fun setupListeners() {
        // Send button
        sendButton.setOnClickListener {
            val text = commandInput.text.toString().trim()
            if (text.isNotEmpty()) {
                sendCommand(text)
            }
        }
        
        // Mic button
        micButton.setOnClickListener {
            startVoiceRecognition()
        }
        
        // Mode switch
        modeSwitch.setOnCheckedChangeListener { _, isChecked ->
            isTypeMode = isChecked
            updateModeUI()
        }
        
        // Settings button
        settingsButton.setOnClickListener {
            showSettingsDialog()
        }
    }
    
    private fun updateModeUI() {
        if (isTypeMode) {
            modeSwitch.text = "Type on PC"
            commandInput.hint = "Text to type on PC..."
            sendButton.text = "TYPE"
        } else {
            modeSwitch.text = "Control PC"
            commandInput.hint = "Command (e.g., 'open chrome')..."
            sendButton.text = "SEND"
        }
    }
    
    private fun sendCommand(text: String) {
        lifecycleScope.launch {
            showLoading(true)
            
            val result = if (isTypeMode) {
                commandSender.sendTypeText(text)
            } else {
                commandSender.sendCommand(text)
            }
            
            showLoading(false)
            
            when (result) {
                is CommandSender.Result.Success -> {
                    showToast(result.message)
                    commandInput.text.clear()
                }
                is CommandSender.Result.Error -> {
                    showToast(result.message)
                }
            }
        }
    }
    
    private fun startVoiceRecognition() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-US")
            putExtra(RecognizerIntent.EXTRA_PROMPT, if (isTypeMode) "Speak to type..." else "Speak command...")
        }
        
        try {
            startActivityForResult(intent, SPEECH_REQUEST_CODE)
        } catch (e: Exception) {
            showToast("Speech recognition not available")
        }
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        if (requestCode == SPEECH_REQUEST_CODE && resultCode == RESULT_OK) {
            val matches = data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            matches?.firstOrNull()?.let { spokenText ->
                commandInput.setText(spokenText)
                // Auto-send after voice input
                sendCommand(spokenText)
            }
        }
    }
    
    private fun showSettingsDialog() {
        val editText = EditText(this).apply {
            setText(ApiClient.getBaseUrl())
            hint = "http://192.168.1.100:5000/"
        }
        
        AlertDialog.Builder(this)
            .setTitle("PC Server Address")
            .setView(editText)
            .setPositiveButton("Save") { _, _ ->
                val url = editText.text.toString()
                if (url.isNotBlank()) {
                    ApiClient.setBaseUrl(url)
                    saveSettings()
                    checkConnection()
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
    
    private fun checkConnection() {
        lifecycleScope.launch {
            val isConnected = commandSender.checkStatus()
            updateStatus(isConnected)
        }
    }
    
    private fun updateStatus(connected: Boolean) {
        statusText.text = if (connected) "🟢 Connected" else "🔴 Disconnected"
    }
    
    private fun showLoading(show: Boolean) {
        sendButton.isEnabled = !show
        micButton.isEnabled = !show
        // Could add progress bar here
    }
    
    private fun showToast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
    
    private fun checkPermissions() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) 
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.RECORD_AUDIO),
                PERMISSION_REQUEST_CODE
            )
        }
    }
    
    private fun loadSettings() {
        val prefs = getSharedPreferences("jarvis_prefs", MODE_PRIVATE)
        val savedUrl = prefs.getString("server_url", "http://192.168.1.100:5000/")
        ApiClient.setBaseUrl(savedUrl!!)
        checkConnection()
    }
    
    private fun saveSettings() {
        val prefs = getSharedPreferences("jarvis_prefs", MODE_PRIVATE)
        prefs.edit().putString("server_url", ApiClient.getBaseUrl()).apply()
    }
    
    override fun onResume() {
        super.onResume()
        checkConnection()
    }
}