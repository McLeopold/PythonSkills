from math import sqrt

class MatrixError(Exception):
    pass

class Matrix(list):

    ERROR_TOLERANCE = 0.00000000000001

    def __init__(self, rows, cols, data=None):
        self.rows = rows
        self.cols = cols
        if data is not None:
            for row in data:
                self.append(row[:])

    @staticmethod
    def from_column_values(rows, columns, column_values):
        return Matrix(columns, rows, column_values).transpose()

    @staticmethod
    def from_rows_columns(rows, cols, *values):
        m = []
        for row in range(rows):
            m.append([])
            for col in range(cols):
                m[row].append(values[row * rows + col])
        return Matrix(rows, cols, m)

    def transpose(self):
        return Matrix(self.cols, self.rows, map(lambda * row: list(row), *self))

    def is_square(self):
        return self.rows == self.cols and self.rows > 0

    def determinant(self):
        if not self.is_square():
            raise MatrixError("Matrix is not square")
        if self.rows == 1:
            return self[0][0]
        elif self.rows == 2:
            return self[0][0] * self[1][1] - self[0][1] * self[1][0]
        else:
            result = 0.0
            for current_column in range(self.cols):
                first_row_col_value = self[0][current_column]
                cofactor = self.cofactor(0, current_column)
                item_to_add = first_row_col_value * cofactor
                result += item_to_add

        return result

    def adjugate(self):
        if not self.is_square():
            raise MatrixError("Matrix is not square")

        if self.rows == 2:
            return SquareMatrix(self[1][1], -self[0][1], -self[1][0], self[0][0])
        else:
            result = []
            for col in range(self.cols):
                result.append([])
                for row in range(self.rows):
                    result[col].append(self.cofactor(row, col))
        return Matrix(self.cols, self.rows, result)

    def inverse(self):
        if self.rows == 1 and self.cols == 1:
            return SquareMatrix(1.0 / self[0][0])
        determinant_inverse = 1.0 / self.determinant()
        adjugate = self.adjugate()
        return self.scalar_multiply(determinant_inverse, adjugate)

    @staticmethod
    def scalar_multiply(scalar_value, matrix):
        new_values = []
        for row in range(matrix.rows):
            new_values.append([])
            for col in range(matrix.cols):
                new_values[row].append(scalar_value * matrix[row][col])
        return Matrix(matrix.rows, matrix.cols, new_values)

    def __add__(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise MatrixError("Matrices must be of the same size")
        rows, cols = self.rows, other.cols
        m = []
        for row in range(rows):
            m.append([])
            for col in range(cols):
                m[row].append(self[row][col] + other[row][col])
        return Matrix(rows, cols, m)

    def __mul__(self, other):
        if (not hasattr(other, 'rows') or
                not hasattr(other, 'cols')):
            # assume scalar
            new_values = []
            for row in range(self.rows):
                new_values.append([])
                for col in range(self.cols):
                    new_values[row].append(other * self[row][col])
            return Matrix(self.rows, self.cols, new_values)
        else:
            if self.cols != other.rows:
                raise MatrixError("The width of the left matrix must match the height of the right matrix")
            rows, cols = self.rows, other.cols
            m = []
            for row in range(rows):
                m.append([])
                for col in range(cols):
                    v = 0.0
                    for i in range(self.cols):
                        v += self[row][i] * other[i][col]
                    m[row].append(v)
            return Matrix(rows, cols, m)
    __rmul__ = __mul__

    def minor_matrix(self, row_to_remove, col_to_remove):
        m = []
        for row in range(self.rows):
            if row == row_to_remove:
                continue
            m.append([])
            for col in range(self.cols):
                if col == col_to_remove:
                    continue
                m[-1].append(self[row][col])
        return Matrix(self.rows - 1, self.cols - 1, m)

    def cofactor(self, row_to_remove, col_to_remove):
        if (row_to_remove + col_to_remove) % 2 == 0:
            return self.minor_matrix(row_to_remove, col_to_remove).determinant()
        else:
            return -1.0 * self.minor_matrix(row_to_remove, col_to_remove).determinant()

    def __eq__(self, other):
        if other is None:
            return False
        if self.rows != other.rows or self.cols != other.cols:
            return False
        for row in range(self.rows):
            for col in range(self.cols):
                delta = abs(self[row][col] - other[row][col])
                if delta > Matrix.ERROR_TOLERANCE:
                    return False
        return True

class Vector(Matrix):
    def __init__(self, values):
        column_values = []
        for value in values:
            column_values.append([value])
        Matrix.__init__(self, len(values), 1, column_values)

class SquareMatrix(Matrix):
    def __init__(self, *values):
        rows = cols = int(sqrt(len(values)))
        data = []
        for row in range(rows):
            data.append([])
            for col in range(cols):
                data[row].append(values[row * rows + col])
        Matrix.__init__(self, rows, cols, data)

class DiagonalMatrix(Matrix):
    def __init__(self, values):
        rows = cols = len(values)
        data = []
        for row in range(rows):
            data.append([0] * cols)
            data[row][row] = values[row]
        Matrix.__init__(self, rows, cols, data)

class IdentityMatrix(DiagonalMatrix):
    def __init__(self, rows):
        DiagonalMatrix.__init__(self, [1] * rows)

if __name__ == "__main__":
    m = Matrix(2, 2, [[1, 2], [3, 4]])
    print m.transpose()
