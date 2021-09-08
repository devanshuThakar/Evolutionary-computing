function y=Rastring(A, n, X)
y=A*n + sum(X.*X - A*cos(2*pi*X));
end
