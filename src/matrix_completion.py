import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.decomposition import TruncatedSVD
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

def svd_matrix_completion(matrix, rank=None, tol=1e-5, max_iter=100):
    """
    Complète une matrice avec des valeurs manquantes en utilisant la décomposition SVD tronquée.
    
    :param matrix: La matrice d'entrée avec des NaN pour les valeurs manquantes
    :param rank: Le rang de l'approximation (par défaut, min(n_rows, n_cols) / 2)
    :param tol: La tolérance pour la convergence
    :param max_iter: Le nombre maximum d'itérations
    :return: La matrice complétée
    """
    if rank is None:
        rank = min(matrix.shape) // 2

    # Initialiser les valeurs manquantes avec la moyenne de chaque colonne
    imputer = SimpleImputer(strategy='mean')
    filled_matrix = imputer.fit_transform(matrix)

    mask = np.isnan(matrix)
    for _ in range(max_iter):
        old_matrix = filled_matrix.copy()
        
        # Appliquer SVD tronquée
        svd = TruncatedSVD(n_components=rank)
        svd.fit(filled_matrix)
        filled_matrix = svd.inverse_transform(svd.transform(filled_matrix))
        
        # Remplacer les valeurs connues
        filled_matrix[~mask] = matrix[~mask]
        
        # Vérifier la convergence
        if np.linalg.norm(filled_matrix - old_matrix) < tol:
            break

    return filled_matrix

def iterative_imputer_completion(matrix):
    """
    Complète une matrice avec des valeurs manquantes en utilisant l'imputation itérative.
    
    :param matrix: La matrice d'entrée avec des NaN pour les valeurs manquantes
    :return: La matrice complétée
    """
    imputer = IterativeImputer(max_iter=10, random_state=0)
    return imputer.fit_transform(matrix)

# Exemple d'utilisation
if __name__ == "__main__":
    
    # data/synthesis_data/synthesis.csv
    matrix_orig = pd.read_csv("data/synthesis_data/synthesis.csv", index_col=0)
    print("Matrice originale:")
    print(matrix_orig)
    cols_to_drop = ["Classe", "Groupe"]
    matrix_orig = matrix_orig.drop(cols_to_drop, axis=1).to_numpy()
    # randomly about 1% of the values to NaN
    np.random.seed(0)
    mask = np.random.rand(*matrix_orig.shape) < 0.3
    matrix_nan = matrix_orig.copy()
    matrix_nan[mask] = np.nan
    print("\nMatrice avec des valeurs manquantes:")
    print(matrix_nan)


    completed_matrix_svd = svd_matrix_completion(matrix_nan)
    print("\nMatrice complétée avec SVD:")
    # print(completed_matrix_svd)

    completed_matrix_iterative = iterative_imputer_completion(matrix_nan)
    print("\nMatrice complétée avec imputation itérative:")
    # print(completed_matrix_iterative)

    # Comparer les résultats sur des colonnes aléatoires
    # set seed for reproducibility
    np.random.seed(10)
    random_cols = np.random.choice(matrix_nan.shape[1], 10, replace=False)
    for col in random_cols:
        print(f"\nComparaison pour la colonne {col}:")
        # Créer un DataFrame pour une meilleure présentation
        # print("matrice_nan")
        # print(matrix_nan[:, col])
        comparison_df = pd.DataFrame({
            'Valeurs originales': matrix_orig[:, col],
            'Valeurs réelles nan': matrix_nan[:, col],
            'SVD': completed_matrix_svd[:, col],
            'Imputation itérative': completed_matrix_iterative[:, col]
        })
        
        # Afficher uniquement les lignes où il y avait des valeurs manquantes et ou la valeur orinale est connue
        missing_mask = np.isnan(matrix_nan[:, col]) & ~np.isnan(matrix_orig[:, col])
        comparison_df_missing = comparison_df[missing_mask]
        
        # Afficher le DataFrame avec un formatage amélioré
        pd.set_option('display.float_format', '{:.2f}'.format)
        print(comparison_df_missing.to_string(index=False))
        
        # Calculer et afficher les erreurs moyennes
        mse_svd = np.mean((matrix_nan[:, col][~np.isnan(matrix_nan[:, col])] - completed_matrix_svd[:, col][~np.isnan(matrix_nan[:, col])])**2)
        mse_iterative = np.mean((matrix_nan[:, col][~np.isnan(matrix_nan[:, col])] - completed_matrix_iterative[:, col][~np.isnan(matrix_nan[:, col])])**2)
        
        print(f"\nErreur quadratique moyenne (MSE) :")
        print(f"SVD : {mse_svd:.6f}")
        print(f"Imputation itérative : {mse_iterative:.6f}")