
[file,path] = uigetfile(".xlsx",'Select Data to be Analyzed');
fpath = append(path,file);
PTAdata = xlsread(fpath,'PTA All sessions')
PLPFCdata = xlsread(fpath,'PLPFC All sessions')

numel(PTAdata(:,1))
xcorrmatrix = [];
maxmatrix = [];

for j = 1:numel(PTAdata(1,:))
    for rng = ["all", 50, 150]
        if rng == "all"
            lowerrng = 1;
            upperrng = 200;
        else
            lowerrng = str2num(rng);
            upperrng = lowerrng + 50;
        end
        for i = 1:(numel(PTAdata(1,:))) %Individual XCorrels
            x = PTAdata(lowerrng:upperrng,i);
            y = PLPFCdata(lowerrng:upperrng,i);
            [r,lags] = xcorr(x,y,'coeff');
            z = atanh(r);
            z = r;
            xcorrmatrix = [xcorrmatrix z];   
            maxmatrix = [maxmatrix max(z)];
        end
        lags = rot90(lags,-1);
        xcorrmatrix = [lags xcorrmatrix];
        csvwrite(append(path,strcat("xcorrLMP3indv",num2str(rng),extractBetween(file,15,22),".csv")),xcorrmatrix);
        csvwrite(append(path,strcat("xcorrLMP3indvMAX",num2str(rng),extractBetween(file,15,22),".csv")),maxmatrix);
        xcorrmatrix = [];
        maxmatrix = [];
    end
end
disp("Done!");
