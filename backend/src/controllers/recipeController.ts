import { Request, Response } from 'express';
import { Recipe } from '../models/Recipe';

// Hämta alla recept
export const getRecipes = async (req: Request, res: Response) => {
  const recipes = await Recipe.find().populate('createdBy', 'email');
  res.json(recipes);
};

// Skapa nytt recept
export const createRecipe = async (req: Request, res: Response) => {
  try {
    const { title, ingredients, instructions, userId } = req.body;
    const newRecipe = await Recipe.create({
      title,
      ingredients,
      instructions,
      createdBy: userId
    });
    res.status(201).json(newRecipe);
  } catch (err) {
    res.status(500).json({ error: 'Kunde inte spara recept' });
  }
};

// Uppdatera/ändra ett recept i MongoDB
export const updateRecipe = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { title, ingredients, instructions, userId } = req.body;

    const updatedRecipe = await Recipe.findByIdAndUpdate(
      id,
      {
        title,
        ingredients,
        instructions,
        updatedBy: userId // Spara vem som gjorde ändringen
      },
      { new: true } // Returnerar det uppdaterade dokumentet
    );

    res.json(updatedRecipe);
  } catch (err) {
    res.status(500).json({ error: 'Kunde inte uppdatera receptet' });
  }
};