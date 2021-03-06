import argparse
import secrets
import struct

class Polynomial:
  """Represents a simple n degree polynomial polynomial"""

  def __init__(self, coefficients):
    """Initializes coefficients of the polynomial, in increasing order"""
    self._coefficients = coefficients
    self._coefflength = len(coefficients)
    self.degree = len(coefficients) - 1
    if self.degree < 0:
      raise ValueError("coefficients must not be empty")
    self.derivative = None
  
  def get_coeffs(self):
    return self._coefficients[:]

  def deriv(self):
    """Returns the derivative of the polynomial"""
    if self.derivative :
      return self.derivative
    deriv_coefficients = [self._coefficients[i] * i for i in range(1, self._coefflength)]
    self.derivative = Polynomial(deriv_coefficients)
    return self.derivative

  def root(self, x0, epsilon, max_iter, Df=None):
    """Returns a root of the polynomial using Newton's Method"""
    if not Df :
      Df = self.deriv()
    xn = x0
    for n in range(0,max_iter):
      fxn = self(xn)
      if abs(fxn) < epsilon:
        return xn
      Dfxn = Df(xn)
      if Dfxn == 0:
        raise ValueError('Zero derivative. No solution found.')
      xn = xn - fxn/Dfxn
    raise RuntimeError('Exceeded maximum iterations. No solution found.')
    return None

  def __sub__(self, right):
    lowest = min(self._coefflength, right._coefflength)
    new_coefficients = [self._coefficients[i] - right._coefficients[i] for i in range(lowest)]
    if self._coefflength < right._coefflength :
      new_coefficients.extend([-1 * right._coefficients[i] for i in range(lowest, right._coefflength)])
    if self._coefflength > right._coefflength :
      new_coefficients.extend([self._coefficients[i] for i in range(lowest, self._coefflength)])
    return Polynomial(new_coefficients)

  def __call__(self, x):
    return sum(self._coefficients[i] * x**i for i in range(self._coefflength))
    

  def __repr__(self):
    out = ""
    for i in range(1, self._coefflength):
      if self._coefficients[i] != 0:
        if self._coefficients[i] > 0:
          out += " + "
        else:
          out += " - "
        out +=  ("" if abs(self._coefficients[i]) == 1 else str(abs(self._coefficients[i]))) + "x^" + str(i)
    out = out[3:] if self._coefficients[0] == 0 else str(self._coefficients[0]) + out 
    return out

class PolyEncryption:
  """Performs symmetric encryption with a secret polynomial(Polynomial) read from file or object"""

  def __init__(self, filename=None, polynomial=None):
    if filename:
      self.read_poly(filename)
    elif polynomial:
      self.polynomial = polynomial
      self.polyderiv = polynomial.deriv()

  def write_poly(self, filename):
    coeffs = self.polynomial.get_coeffs()
    with open(filename, "wb") as fout:
      fout.write(struct.pack('B'*len(coeffs), *coeffs))

  def read_poly(self, filename):
    with open(filename, "rb") as fin:
      self.polynomial = Polynomial([coeff[0] for coeff in struct.iter_unpack('B', fin.read())])
      self.polyderiv = self.polynomial.deriv()

  def encrypt(self, filename, x0, epsilon, max_iter):
    if not self.polynomial:
      raise ValueError("No polynomial loaded")
    roots = []
    with open(filename, "rb") as fin:
      all_bytes = fin.read()
      for b in all_bytes:
        new_poly = self.polynomial - Polynomial([b])
        roots.append(new_poly.root(x0, epsilon, max_iter, self.polyderiv))
    with open(filename + ".enc", "wb") as fout:
      fout.write(struct.pack('q', x0))
      fout.write(struct.pack('d', epsilon))
      fout.write(struct.pack('Q', max_iter))
      s = struct.pack('d'*len(roots), *roots)
      fout.write(s)
    
  def decrypt(self, filename):
    if not self.polynomial:
      raise ValueError("No polynomial loaded")
    with open(filename, "rb") as fin:
      x0 = struct.unpack('q', fin.read(8))
      epsilon = struct.unpack('d', fin.read(8))
      max_iter = struct.unpack('Q', fin.read(8))
      s = bytes(int(round(self.polynomial(root[0]))) for root in struct.iter_unpack('d', fin.read()))
      with open(filename + ".dec", "wb") as fout:
        fout.write(s)


def main():
  my_parser = argparse.ArgumentParser(description="Newton's method based encryption")
  my_parser.add_argument('--genkey', action='store', help="Generate a new key")
  my_parser.add_argument('--keyfile', action='store', help="The keyfile to encrypt decrypt with")
  my_parser.add_argument('--encrypt', action='store', help="The file to encrypt")
  my_parser.add_argument('--decrypt', action='store', help="The file to decrypt")
  args = my_parser.parse_args()
  if args.genkey:
    poly = Polynomial([secrets.randbits(8) for i in range(32)])
    poly_enc = PolyEncryption(None, poly)
    poly_enc.write_poly(args.genkey)
  elif args.keyfile:
    poly_enc = PolyEncryption(args.keyfile)
    if args.encrypt:
      poly_enc.encrypt(args.encrypt, 0, 1e-10, 1000)
    elif args.decrypt:
      poly_enc.decrypt(args.decrypt)
    
if __name__ == "__main__":
  main()
