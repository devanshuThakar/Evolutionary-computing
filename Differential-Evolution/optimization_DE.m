clc;
clear all;
close all;

A = 10;
n = 2;
CP = 0.5; % Cross-over Probability
individuals = 10;
scaling_fact = 0.5;
tot_iter=500;
pop = (rand(individuals,2)-0.5)*2*5.12;

%% Inital evaluation of fitness
for i=1:individuals
    pop(i,3) = Rastring(A, n, pop(i,1:n));
end
x = 1:individuals;

%% Creating the plot of initial position of individuals
points = 150;
x1 = linspace(-5.12,5.12, points);
x2 = linspace(-5.12,5.12,points);
y = zeros(points, points);

for i=1:numel(x1)
    for j=1:numel(x2)
        y(i,j)=Rastring(10,2,[x1(i), x2(j)]);
    end
end
best = find(pop(:,3)==min(pop(:,3)));

f1= figure('WindowState','maximized');
axis([-5 5 -5 5])
scatter(pop(:,1), pop(:,2), 'filled', 'blue');
hold on;
scatter(pop(best,1), pop(best,2), 'filled', 'red');
title("Plot of initial position of all individuals in XY (2D-plane)");
grid on
grid minor
l1=legend('other individuals', 'best individual');
xlabel('x1')
ylabel('x2')
l1.Location = 'northeastoutside';

f2=figure('WindowState','maximized');
mesh(x1,x2,y)
title("Plot of rastring function along with initial position of individuals");
hold on;
scatter3(pop(:,1), pop(:,2), pop(:,3),'blue','filled');
scatter3(pop(best,1), pop(best,2), pop(best,3),'red','filled');
l2=legend('','other individuals', 'best individual');
l2.Location = 'northeastoutside';
xlabel('x1');
ylabel('x2');
zlabel('f(x)');
grid on

%% Loop for genrataion or iterations
best_array = zeros(tot_iter+1,3);
best_array(1,1:3) = [pop(best,1), pop(best,2), pop(best,3)];
for iter=1:tot_iter
    % Looping over all individuals
    for i=1:individuals
        B = x(~ismember(1:individuals, i));
        idx=randperm(numel(B));
        I1 = B(idx(1));
        I2 = B(idx(2));
        I_mut = B(idx(3));

        diff_vect =  pop(I1,1:n) - pop(I2,1:n);
        diff_vect = diff_vect/norm(diff_vect) * 5.12;
        weight_diff_vect = diff_vect * scaling_fact;

        noisy_vect = weight_diff_vect + pop(I_mut, 1:n);
        noisy_vect = noisy_vect/norm(noisy_vect) * 5.12;
        %Corssover
        prob = rand(1,n) < 0.5;
        trial_vect = pop(i,1:n).*prob + noisy_vect.*(~prob);
        trial_vect(1,n+1) = Rastring(A, n, trial_vect(1:n));

        %Select the better amongst trial vect and traget vect
        if(trial_vect(1,n+1) < pop(i,n+1))
            pop(i,:) = trial_vect(1,:);
        end
    end
    best = find(pop(:,3)==min(pop(:,3)));
    best_array(iter+1,1:3) = [pop(best,1), pop(best,2), pop(best,3)];
end

%% Loop for moving the point
points = 150;
max_XY=5.12;
x1 = linspace(-max_XY,max_XY, points);
x2 = linspace(-max_XY,max_XY,points);
y = zeros(points, points);

for i=1:numel(x1)
    for j=1:numel(x2)
        y(i,j)=Rastring(10,2,[x1(i), x2(j)]);
    end
end

f3=figure('WindowState','maximized');
set(gca,'XLim',[-max_XY max_XY], 'YLim', [-max_XY max_XY]);
mesh(x1,x2,y)
hold on;
pbest=scatter3(best_array(1,1), best_array(1,2), best_array(1,3), 30,'red','filled');
xlabel('x1');
ylabel('x2');
zlabel('f(x)');
f3_annot = annotation('textbox', [0.75, 0.75, 0.1, 0.1], 'String', "Iteration : " + 0);
tmp=annotation('textbox', [0.45, 0.75, 0.1, 0.1], 'String', "The movement of point will start in " + 3);
for j=5:-1:1
    pause(1);
    tmp.String = "The movement of point will start in " + j;
end
pause(1);
delete(tmp)
for i=2:tot_iter+1
    pbest.XData = best_array(i,1);
    pbest.YData = best_array(i,2);
    pbest.ZData = best_array(i,3);
    f3_annot.String = "Iteration : " + (i-1);
    pause(0.1);
end