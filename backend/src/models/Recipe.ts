import { Schema, model } from 'mongoose';

const recipeSchema = new Schema({
  title: { type: String, required: true },
  ingredients: { type: [String], required: true },
  instructions: { type: String, required: true },
  createdBy: { type: Schema.Types.ObjectId, ref: 'User' },
  updatedBy: { type: Schema.Types.ObjectId, ref: 'User' } // Sparar vem som senast ändrade
}, { timestamps: true });

export const Recipe = model('Recipe', recipeSchema);