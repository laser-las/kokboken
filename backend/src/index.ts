import express from 'express';
import cors from 'cors';
import mongoose from 'mongoose';
import dotenv from 'dotenv';

import { register, login } from './controllers/authController';
import { getRecipes, createRecipe, updateRecipe } from './controllers/recipeController';

dotenv.config();

const app = express();
app.use(cors({ origin: 'http://localhost:5173' }));
app.use(express.json());

// Koppla till MongoDB
const mongoUri = process.env.MONGODB_URI || '';
mongoose.connect(mongoUri)
  .then(() => console.log('Ansluten till MongoDB!'))
  .catch((err) => console.error('MongoDB anslutningsfel:', err));

// Auth routes
app.post('/api/auth/register', register);
app.post('/api/auth/login', login);

// Recept routes
app.get('/api/recipes', getRecipes);
app.post('/api/recipes', createRecipe);
app.put('/api/recipes/:id', updateRecipe); // För att ändra recept

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server körs på port ${PORT}`));