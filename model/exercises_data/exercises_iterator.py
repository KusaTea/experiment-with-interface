from random import shuffle

class ExercisesIterator:

    def __init__(self, repeats_number: int, number_of_exercises: int):

        self.exercises_indeces = list(range(1, number_of_exercises)) * repeats_number
        shuffle(self.exercises_indeces)
    
    def __len__(self):
        return len(self.exercises_indeces)


    def __iter__(self):
        return self
    

    def __next__(self):
        if len(self.exercises_indeces) > 0:
            self.current_exercise_idx = self.exercises_indeces.pop()
            return self.current_exercise_idx
        
        else:
            raise StopIteration
        
