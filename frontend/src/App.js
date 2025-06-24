import React, { useState } from 'react';
import { Container, Typography, Box, Button, TextField, Paper } from '@mui/material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [file, setFile] = useState(null);
  const [filename, setFilename] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [summary, setSummary] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);

  const handleFileUpload = async (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE_URL}/upload`, formData);
      setFilename(response.data.filename);
      setFile(selectedFile);
    } catch (error) {
      alert('Error uploading file: ' + error.response?.data?.error || error.message);
    } finally {
      setLoading(false);
    }
  };

  const playTextToSpeech = async (text) => {
    if (!text) {
      alert('No text available to play!');
      return;
    }

    try {
      setLoading(true);
      console.log('Sending text to speech API:', text.substring(0, 100) + '...'); // Debug log
      
      const response = await axios.post(
        `${API_BASE_URL}/synthesize`,
        { text },
        { 
          responseType: 'blob',
          timeout: 30000 // 30 second timeout
        }
      );

      console.log('Received audio response:', response); // Debug log
      console.log('Response size:', response.data.size); // Debug log

      const audioBlob = new Blob([response.data], { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);
      setAudioUrl(audioUrl);

      const audio = new Audio(audioUrl);
      
      // Add event listeners for better debugging
      audio.onloadstart = () => console.log('Audio loading started');
      audio.oncanplay = () => console.log('Audio can play');
      audio.onplay = () => {
        console.log('Audio started playing');
        setIsPlaying(true);
      };
      
      audio.onended = () => {
        console.log('Audio playback ended');
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
        setAudioUrl(null);
      };
      
      audio.onerror = (e) => {
        console.error('Audio error:', e);
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
        setAudioUrl(null);
        alert('Error playing audio: ' + e.message);
      };
      
      // Start playing
      await audio.play();
      
    } catch (error) {
      console.error('Error in playTextToSpeech:', error); // Debug log
      console.error('Error response:', error.response); // Debug log
      
      let errorMessage = 'Error playing audio: ';
      if (error.response) {
        // Server responded with error status
        if (error.response.data instanceof Blob) {
          // Try to read the error message from blob
          const reader = new FileReader();
          reader.onload = () => {
            try {
              const errorData = JSON.parse(reader.result);
              alert(errorMessage + errorData.error);
            } catch {
              alert(errorMessage + 'Server error');
            }
          };
          reader.readAsText(error.response.data);
        } else {
          errorMessage += error.response.data?.error || error.response.statusText;
          alert(errorMessage);
        }
      } else if (error.request) {
        // Network error
        errorMessage += 'Network error - please check your connection';
        alert(errorMessage);
      } else {
        // Other error
        errorMessage += error.message;
        alert(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const playSummaryAudio = async () => {
    if (!summary) {
      alert('Please generate a summary first!');
      return;
    }
    await playTextToSpeech(summary);
  };

  const playExtractedTextAudio = async () => {
    if (!extractedText) {
      alert('Please extract text first!');
      return;
    }
    await playTextToSpeech(extractedText);
  };

  const extractText = async () => {
    if (!filename) {
      alert('Please upload a file first!');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE_URL}/extract`, { filename });
      setExtractedText(response.data.text);
    } catch (error) {
      alert('Error extracting text: ' + error.response?.data?.error || error.message);
    } finally {
      setLoading(false);
    }
  };

  const summarizeText = async () => {
    if (!extractedText) {
      alert('Please extract text first!');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE_URL}/summarize`, { text: extractedText });
      setSummary(response.data.summary);
    } catch (error) {
      alert('Error generating summary: ' + error.response?.data?.error || error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        📖 Smart Accessibility Reader
      </Typography>
      
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>📄 Upload Document</Typography>
        <Button
          variant="contained"
          component="label"
          fullWidth
        >
          Choose File
          <input
            type="file"
            hidden
            accept="image/*"
            onChange={handleFileUpload}
          />
        </Button>
        {file && <Typography sx={{ mt: 1 }}>Selected file: {file.name}</Typography>}
      </Box>

      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom>🧠 Actions</Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button variant="contained" onClick={extractText} disabled={!filename || loading}>
            🔍 Extract Text
          </Button>
          <Button variant="contained" onClick={summarizeText} disabled={!extractedText || loading}>
            📝 Summarize
          </Button>
          <Button variant="contained" onClick={playExtractedTextAudio} disabled={!extractedText || loading}>
            🔊 Listen to Text {isPlaying && '(Playing...)'}
          </Button>
          <Button variant="contained" onClick={playSummaryAudio} disabled={!summary || loading}>
            🔊 Listen to Summary {isPlaying && '(Playing...)'}
          </Button>
        </Box>
      </Box>

      {extractedText && (
        <Paper sx={{ p: 2, mb: 4 }}>
          <Typography variant="h5" gutterBottom>📄 Extracted Text</Typography>
          <TextField
            multiline
            rows={6}
            fullWidth
            value={extractedText}
            disabled
          />
        </Paper>
      )}

      {summary && (
        <Paper sx={{ p: 2, mb: 4 }}>
          <Typography variant="h5" gutterBottom>✍️ Summary</Typography>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {summary}
          </Typography>
        </Paper>
      )}
    </Container>
  );
}

export default App;
