class MatrixError(Exception):
    pass


class Matrix(list):

    ERROR_TOLERANCE = 0.00000000000001

    def __init__(self, data):
        rows = len(data)
        cols = len(data[0]) if rows > 0 else 0
        self.shape = rows, cols
        for row in data:
            self.append(row[:])

    def transpose(self):
        return Matrix(list(map(lambda * row: list(row), *self)))

    def is_square(self):
        return self.shape[0] == self.shape[1] and self.shape[0] > 0

    def determinant(self):
        if not self.is_square():
            raise MatrixError("Matrix is not square")
        if self.shape == (1, 1):
            return self[0][0]
        elif self.shape == (2, 2):
            return self[0][0] * self[1][1] - self[0][1] * self[1][0]
        else:
            result = 0.0
            for current_column in range(self.shape[1]):
                first_row_col_value = self[0][current_column]
                cofactor = self.cofactor(0, current_column)
                item_to_add = first_row_col_value * cofactor
                result += item_to_add

        return result

    def adjugate(self):
        if not self.is_square():
            raise MatrixError("Matrix is not square")

        if self.shape == (2, 2):
            return Matrix([[self[1][1], -self[0][1]], [-self[1][0], self[0][0]]])
        else:
            result = []
            for col in range(self.shape[1]):
                result.append([])
                for row in range(self.shape[0]):
                    result[col].append(self.cofactor(row, col))
        return Matrix(result)

    def inverse(self):
        if self.shape == (1, 1):
            return Matrix([[1.0 / self[0][0]]])
        determinant_inverse = 1.0 / self.determinant()
        adjugate = self.adjugate()
        return determinant_inverse * adjugate

    def __add__(self, other):
        if self.shape != other.shape:
            raise MatrixError("Matrices must be of the same size")
        m = []
        for row in range(self.shape[0]):
            m.append([])
            for col in range(self.shape[1]):
                m[row].append(self[row][col] + other[row][col])
        return Matrix(m)

    def __mul__(self, other):
        if not hasattr(other, 'shape'):
            # assume scalar
            new_values = []
            for row in range(self.shape[0]):
                new_values.append([])
                for col in range(self.shape[1]):
                    new_values[row].append(other * self[row][col])
            return Matrix(new_values)
        else:
            if self.shape[1] != other.shape[0]:
                raise MatrixError("The width of the left matrix must match the height of the right matrix")
            m = []
            for row in range(self.shape[0]):
                m.append([])
                for col in range(other.shape[1]):
                    v = 0.0
                    for i in range(self.shape[1]):
                        v += self[row][i] * other[i][col]
                    m[row].append(v)
            return Matrix(m)
    __rmul__ = __mul__

    def minor_matrix(self, row_to_remove, col_to_remove):
        m = []
        for row in range(self.shape[0]):
            if row == row_to_remove:
                continue
            m.append([])
            for col in range(self.shape[1]):
                if col == col_to_remove:
                    continue
                m[-1].append(self[row][col])
        return Matrix(m)

    def cofactor(self, row_to_remove, col_to_remove):
        if (row_to_remove + col_to_remove) % 2 == 0:
            return self.minor_matrix(row_to_remove, col_to_remove).determinant()
        else:
            return -1.0 * self.minor_matrix(row_to_remove, col_to_remove).determinant()

    def __eq__(self, other):
        if other is None:
            return False
        if self.shape != other.shape:
            return False
        for row in range(self.shape[0]):
            for col in range(self.shape[1]):
                delta = abs(self[row][col] - other[row][col])
                if delta > Matrix.ERROR_TOLERANCE:
                    return False
        return True
