clear all; close all;
data1 = csvread('data1.txt'); data1 = data1(:, 1);
data2 = csvread('data2.txt'); data2 = data2(:, 1);

T = 0.025; % 25ms sampling rate
Fs = 1 / T; % sampling frequency in Hz
N1 = size(data1, 1);
N2 = size(data2, 1);

fft1 = fftshift(abs(fft(data1)));
fft2 = fftshift(abs(fft(data2)));

f_ax1 = [(-N1 / 2):(N1 / 2 - 1)] * Fs / N1;
f_ax2 = [(-N2 / 2):(N2 / 2 - 1)] * Fs / N2;

figure(1); plot(f_ax1, fft1);
figure(2); plot(f_ax2, fft2);

% zero data and see what it looks like then

data1_zeroed = data1 - data1(1);
data2_zeroed = data2 - data2(1);

fft1_zeroed = fftshift(abs(fft(data1_zeroed)));
fft2_zeroed = fftshift(abs(fft(data2_zeroed)));

figure(3); plot(f_ax1, fft1_zeroed);
figure(4); plot(f_ax2, fft2_zeroed);


