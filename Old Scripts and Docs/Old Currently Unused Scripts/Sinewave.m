x = linspace(1,200,200);
t = x' .* ones(200,10);
t = t./10
rng default
sig1_denoised_resid = sin(2*pi.*(t)); + randn(size(t));
sig2_denoised_resid = sin(2*pi*(39/40).*(t+0.5)); + randn(size(t));

j = 1;
z = rot90(sig1_denoised_resid(191:200,j));
y = rot90(sig2_denoised_resid(191:200,j));
[r,lags] = xcorr(z,y); % This performs the xcorrelation
lags = rot90(lags,-1);
r = rot90(r,-1);

hold on
plot(x,sig1_denoised_resid)
plot(x,sig2_denoised_resid)
hold off
plot(lags,r)


for j = 1:numel(sig1_denoised_resid(1,:)) % Iterate through every column within the matrix
    x = rot90(sig1_denoised_resid(lowerrng:upperrng,j));
    y = rot90(sig2_denoised_resid(lowerrng:upperrng,j));
    [r,lags] = xcorr(x,y); % This performs the xcorrelation
    lags = rot90(lags,-1);
    r = rot90(r,-1);
    %             r = (r-mean(r))/std(r);
    z = [z r]; % The z matrix collects the cross correlation of each analysis
    plot(lags,r)
    hold on
end