

x = linspace(1,200,200);
t = x' .* ones(200,10);
t = t./10;
rng default
sig1_denoised_resid = sin(2*pi.*(t)); + randn(size(t));
sig2_denoised_resid = sin(2*pi*(39/40).*(t+0.5)); + randn(size(t));
MMsig1_str = "signal 1";
MMsig2_str = "Signal 2";

hold on
plot(x,sig1_denoised_resid)
plot(x,sig2_denoised_resid)
hold off

xcorrmultiout = {}; % We have to use a cell array for xcorrmultiout, as the matrix outputs will be differently sized depending on the window size.
xcorrmultioutmaxima = {};
xcorrindex = 0;
rnglist = {};
for j = 1:20
    g = 1+((j-1)*10);
    rnglist = [rnglist j]; % -1 is used as a substitute for "all"
end
rngnames = cellfun(@num2str,rnglist,'un',0);
for i = 1:length(rnglist) % Iterate through each of the windows of interest
    rng = rnglist{i};
    xcorrindex = xcorrindex + 1; % This index refers to the "page" of the matlab matrix, each window is placed on a different page.
    if rng == -1
        lowerrng = 1;
        upperrng = 200;
    else
        lowerrng = (rng-1)*10+1;
        upperrng = lowerrng +  9; % Set the size of the window of interest
    end
    z = []; % IMPORTANT; this prevents overflow of previous analyses into the z variable
    for j = 1:numel(sig1_denoised_resid(1,:)) % Iterate through every column within the matrix

        x = rot90(sig1_denoised_resid(lowerrng:upperrng,j));
        y = rot90(sig2_denoised_resid(lowerrng:upperrng,j));
                plot(lowerrng:upperrng,x)
        hold on
        plot(lowerrng:upperrng,y)
        [r,lags] = xcorr(x,y); % This performs the xcorrelation
        lags = rot90(lags,-1);
        r = rot90(r,-1);
        %             r = (r-mean(r))/std(r);
        z = [z r]; % The z matrix collects the cross correlation of each analysis
%         plot(lags,r)
%         hold on
    end
    xcorrmultiout{xcorrindex} = [lags z];
    xcorrmultioutmaxima{xcorrindex} = max(z);
end