%% Photometry Regression and Analysis Script
% This script is for Photometry data analysis. The majority of this code can
% be reused for any photometry project, changing only the analysis portion
% of the code. Whenever you change this code you should update this section
% of the comments within the script in addition to the filename. The naming
% convention for this code is:
% PhotomRegressMMv[Version Number]_[Analysis][Initials][Analysis Version Number].m
% Branches/special edits will be marked in the filename via the addition of
% a _[keyword] at the end of the file name accompanied by an explaination
% of the changes HERE:
%
%
%
%
%% Description of Analysis
% Place a quick summary of the analysis being performed in the analysis
% section of the code HERE:
% 
%
%
clear;
%% Identify file paths
% This first section of code exists purely to create a list of all the files
% that will be processed. The intention is for the user to select all the
% .mat files for a particular animal at a time. This code is NOT meant to
% process an entire cohort at once. (Purely due to my laziness, I may do
% something to fix this in the future).
[file,path] = uigetfile(".mat",'Select Data to be Analyzed','MultiSelect','on');
fpath = append(path,file);
fpath = string(fpath');
numfiles = numel(fpath);

%% Create "Master Matrix" Variables
% The next necessary step is to iterate through all the files and create
% "Master Matrices" for each variable stored across all the .mat files. By
% this I mean that I will concatenate the matrices stores within the .mat
% file to create a matrix that is (images)X(Trials) containing all trials.
% All "Master Matrices" will be denoted by the prefix MM

MMcorrsigbr = [];
MMcorrsigpr = [];
MMsig1_br = [];
MMsig1_br_resid = [];
MMsig1_pr = [];
MMsig1_pr_resid = [];
MMsig2_br = [];
MMsig2_br_resid = [];
MMsig2_pr = [];
MMsig2_pr_resid = [];
MMsig1_str = [];
MMsig2_str = [];

%We will now iterate through all the files to assemble the Master Matrices
for i = 1:numfiles
    %Load all the variables from the selected file
    load(fpath(i));
    %Concatenate all the variables from each file onto our Master Matrices
    MMcorrsigbr = [MMcorrsigbr corrsigbr];
    MMcorrsigpr = [MMcorrsigpr corrsigpr];
    MMsig1_br = [MMsig1_br sig1_br];
    MMsig1_br_resid = [MMsig1_br_resid sig1_br_resid];
    MMsig1_pr = [MMsig1_pr sig1_pr];
    MMsig1_pr_resid = [MMsig1_pr_resid sig1_pr_resid];
    MMsig2_br = [MMsig2_br sig2_br];
    MMsig2_br_resid = [MMsig2_br_resid sig2_br_resid];
    MMsig2_pr = [MMsig2_pr sig2_pr];
    MMsig2_pr_resid = [MMsig2_pr_resid sig2_pr_resid];
    MMsig1_str = sig1_str;
    MMsig2_str = sig2_str;
    %Clear all the loaded variables before the next loop
    clear corrsigbr corrsigpr sig1_br sig1_br_resid sig1_pr...
        sig1_pr_resid sig2_br sig2_br_resid sig2_pr sig2_pr_resid...
        sig1_str sig2_str;
end

%% Regression of the photometry signal from the correction fiber signal
% Now that we have all the trials stored in a single variable, we may now
% begin to regress the photometry signal from the correction fiber signal.

% The data is processed in "bins" of n trials. This is to account for long
% term degredation of the signal over time. It has the effect of "smoothing
% out" the data by providing a better baseline for the correction fiber.
% This binsize can be changed by editing the constant below if needed (it
% is recommended but not necissary for your total trials to be divisible by
% this bin size).
binsize = 10;

% Next we must determine the number of bins within the Master Matricies,
% then "reshape" the data for regression such that it is "glued together"
% end to end.
% So if a session has 65 trials, with 100 images per trial,
% the data is going to be stored in 100 x 65 matrices. The binned matrices
% then will be a 1000 x 6 matrices, since 10 trials = 1000 images, and
% there will be 6 bins of ten. The last five remainder trials are the 7th
% and final bin. So for coding, the implementation involves
% finding the remainder of the total number of trials/10, which equals the
% number of trials in the final bin. The matrix is then reshaped for trials
% 1 to (# of Trials - remainder), and the remainder trials are stored in a
% separate array.

[nImgs,nTrials] = size(MMsig1_br);
binr = mod(nTrials,binsize);



if binr ~= 0 % There exist remainder trials
    % Reshape the matrix for for Trials 1 to (# of Trials - remainder)
    sig1_br_r1=reshape(MMsig1_br(:,1:end-binr),nImgs*10,(nTrials-binr)/10);
    sig2_br_r1=reshape(MMsig2_br(:,1:end-binr),nImgs*10,(nTrials-binr)/10);
    sig1_pr_r1=reshape(MMsig1_pr(:,1:end-binr),nImgs*10,(nTrials-binr)/10);
    sig2_pr_r1=reshape(MMsig2_pr(:,1:end-binr),nImgs*10,(nTrials-binr)/10);
    % Reshape the remainder trials into a 1 dimensional array
    sig1_br_r2=reshape(MMsig1_br(:,end-binr+1:end),binr*nImgs,1);
    sig2_br_r2=reshape(MMsig2_br(:,end-binr+1:end),binr*nImgs,1);
    sig1_pr_r2=reshape(MMsig1_pr(:,end-binr+1:end),binr*nImgs,1);
    sig2_pr_r2=reshape(MMsig2_pr(:,end-binr+1:end),binr*nImgs,1);
    % Repeat previous steps for correction signal
    corrsigbr_r1=reshape(MMcorrsigbr(:,1:end-binr),nImgs*10,(nTrials-binr)/10);
    corrsigpr_r1=reshape(MMcorrsigpr(:,1:end-binr),nImgs*10,(nTrials-binr)/10);
    corrsigbr_r2=reshape(MMcorrsigbr(:,end-binr+1:end),binr*nImgs,1);
    corrsigpr_r2=reshape(MMcorrsigpr(:,end-binr+1:end),binr*nImgs,1);
else
    % Reshape the matrix for for Trials 1 to (# of Trials - remainder)
    sig1_br_r1=reshape(MMsig1_br(:,1:end-binr),nImgs*10,(nTrials-binr)/10);
    sig2_br_r1=reshape(MMsig2_br(:,1:end-binr),nImgs*10,(nTrials-binr)/10);
    sig1_pr_r1=reshape(MMsig1_pr(:,1:end-binr),nImgs*10,(nTrials-binr)/10);
    sig2_pr_r1=reshape(MMsig2_pr(:,1:end-binr),nImgs*10,(nTrials-binr)/10);
    % Repeat previous steps for correction signal
    corrsigbr_r1=reshape(MMcorrsigbr(:,1:end-binr),nImgs*10,(nTrials-binr)/10);
    corrsigpr_r1=reshape(MMcorrsigpr(:,1:end-binr),nImgs*10,(nTrials-binr)/10);
end

% Great, now we have the data reshaped! Now we can regress the laser energy
% correction fiber signal from the blue and violet laser signal
% Matlab's regression function requires that the predictors (expected)
% value matrix, which in our case is the correction signal, has a column of
% just 1s for the 1st column.

for k=1:(nTrials-binr)/10 % Loop through each bin of 10 and perform the regression to find the residuals
    [~,~,sig1_br_resid(:,k)]=regress(sig1_br_r1(:,k),[ones(nImgs*10,1) corrsigbr_r1(:,k)]);
    [~,~,sig2_br_resid(:,k)]=regress(sig2_br_r1(:,k),[ones(nImgs*10,1) corrsigbr_r1(:,k)]);
    [~,~,sig1_pr_resid(:,k)]=regress(sig1_pr_r1(:,k),[ones(nImgs*10,1) corrsigpr_r1(:,k)]);
    [~,~,sig2_pr_resid(:,k)]=regress(sig2_pr_r1(:,k),[ones(nImgs*10,1) corrsigpr_r1(:,k)]);
end

if binr ~= 0
    % Find residuals for the final bin
    [~,~,sig1_br_resid_r]=regress(sig1_br_r2,[ones(nImgs*r,1) corrsigbr_r2]);
    [~,~,sig2_br_resid_r]=regress(sig2_br_r2,[ones(nImgs*r,1) corrsigbr_r2]);
    [~,~,sig1_pr_resid_r]=regress(sig1_pr_r2,[ones(nImgs*r,1) corrsigpr_r2]);
    [~,~,sig2_pr_resid_r]=regress(sig2_pr_r2,[ones(nImgs*r,1) corrsigpr_r2]);
end

% Residuals have normal distributions with zero mean but with different
% variances at different values of the predictors. To place the residuals
% on a comparable scale, they need to be studentized, which converts them
% to z-scores. The formula is a little too complex to put here,
% but for further details:
% https://www.mathworks.com/help/stats/residuals.html
% https://www.mathworks.com/help/stats/regress.html?s_tid=doc_ta
% In layman's terms, for any one residual out of all the residuals in the
% regression model, the studentized residual is the raw residual divided by
% the standard deviation of all of the residuals, excluding the observation
% point. So for a set of 4 residuals r1, r2, r3, and r4, r1 studentized =
% r1/std(r2, r3, r4), r2 studentized = r2/std(r1, r3, r4), etc...
% To implement this coding-wise, we take advantage of Matlab's matrix
% calculation capabilities. We go through row by row and calculate the
% standard deviation of each column, with the current row excluded. The
% standard deviations for each residual point are saved to a separate
% matrix, and at the end, we ./ the residual matrices with the std
% matrices.

nVec_sig1_b = [];
nVec_sig2_b = [];
nVec_sig1_p = [];
nVec_sig2_p = [];
std1_b = [];
std2_b = [];
std1_p = [];
std2_p = [];
std1_b_r = [];
std2_b_r = [];
std1_p_r = [];
std2_p_r = [];

% To studentize the residuals, we must determine the standard deviations.
% this for loop accomplishes this.
for k=1:nImgs*10 % Loop through each row in the residual matrices
    nVec_sig1_b=sig1_br_resid; % Copy the residual matrix
    nVec_sig1_b(k,:)=[]; % Delete the current row to exclude the points for the std calculation
    std1_b(k,:)=std(nVec_sig1_b); % Calculate the std for each column.
    
    nVec_sig2_b=sig2_br_resid;
    nVec_sig2_b(k,:)=[];
    std2_b(k,:)=std(nVec_sig2_b);
    
    nVec_sig1_p=sig1_pr_resid;
    nVec_sig1_p(k,:)=[];
    std1_p(k,:)=std(nVec_sig1_p);
    
    nVec_sig2_p=sig2_pr_resid;
    nVec_sig2_p(k,:)=[];
    std2_p(k,:)=std(nVec_sig2_p);
end


sig1_br_resid=sig1_br_resid ./ std1_b; % Convert residuals to studentized z-scores
sig2_br_resid=sig2_br_resid ./ std2_b;
sig1_pr_resid=sig1_pr_resid ./ std1_p;
sig2_pr_resid=sig2_pr_resid ./ std2_p;

% Now we have to determine standard deviations for the remainder trials
if binr ~= 0
    for k=1:nImgs*r
        nVec_sig1_br=sig1_br_resid_r;
        nVec_sig1_br(k,:)=[];
        std1_p_r(k,:)=std(nVec_sig1_br);
        
        nVec_sig2_br=sig2_br_resid_r;
        nVec_sig2_br(k,:)=[];
        std2_b_r(k,:)=std(nVec_sig2_br);
        
        nVec_sig1_pr=sig1_pr_resid_r;
        nVec_sig1_pr(k,:)=[];
        std1_p_r(k,:)=std(nVec_sig1_pr);
        
        nVec_sig2_pr=sig2_pr_resid_r;
        nVec_sig2_pr(k,:)=[];
        std2_p_r(k,:)=std(nVec_sig2_pr);
    end
    
    %Finally, we will studentize the remainder trials
    sig1_br_resid_r=sig1_br_resid_r./std1_b_r;
    sig2_br_resid_r=sig2_br_resid_r./std2_b_r;
    sig1_pr_resid_r=sig1_pr_resid_r./std1_p_r;
    sig2_pr_resid_r=sig2_pr_resid_r./std2_p_r;
end

%% Regression of the violet signal from the blue signal
% The process is similar to above. Note that this setion of the code is
% receiving the data STILL BINNED. The end half of this section of code
% will reshape the data back to the format of (Images)x(Trials).

sig1_denoised_resid = [];
sig2_denoised_resid = [];
sig1_denoised_resid_r = [];
sig2_denoised_resid_r = [];

% Perform the regression.
for k=1:(nTrials-binr)/10
    [~,~,sig1_denoised_resid(:,k)]=regress(sig1_br_resid(:,k),[ones(nImgs*10,1) sig1_pr_resid(:,k)]);
    [~,~,sig2_denoised_resid(:,k)]=regress(sig2_br_resid(:,k),[ones(nImgs*10,1) sig2_pr_resid(:,k)]);
end

if binr ~= 0
    [~,~,sig1_denoised_resid_r]=regress(sig1_br_resid_r,[ones(nImgs*r,1) sig1_pr_resid_r]);
    [~,~,sig2_denoised_resid_r]=regress(sig2_br_resid_r,[ones(nImgs*r,1) sig2_pr_resid_r]);
end

% Determine standard deviations for studentization
nVec_sig1 = [];
nVec_sig2 = [];
nVec_sig1_r = [];
nVec_sig2_r = [];
std1_dn = [];
std2_dn = [];
std1_dn_r = [];
std2_dn_r = [];

for k=1:nImgs*10
    
    nVec_sig1=sig1_denoised_resid;
    nVec_sig1(k,:)=[];
    std1_dn(k,:)=std(nVec_sig1);
    
    nVec_sig2=sig2_denoised_resid;
    nVec_sig2(k,:)=[];
    std2_dn(k,:)=std(nVec_sig2);
    
end
sig1_denoised_resid = sig1_denoised_resid ./ std1_dn;
sig2_denoised_resid = sig2_denoised_resid ./ std2_dn;

if binr ~= 0
    for k = 1:nImgs*binr
        nVec_sig1_r = sig1_denoised_resid_r;
        nVec_sig1_r(k,:) = [];
        std1_dn_r(k,:)=std(nVec_sig1_r);
        
        nVec_sig2_r = sig2_denoised_resid_r;
        nVec_sig2_r(k,:) = [];
        std2_dn_r(k,:)=std(nVec_sig2_r);
    end
    sig1_denoised_resid_r = sig1_denoised_resid_r ./ std1_dn_r;
    sig2_denoised_resid_r = sig2_denoised_resid_r ./ std2_dn_r;
end

%% Reshape the Data back into MM format
% This part of the code merely puts the data back into the same MM format,
% with each column being one trial.
sig1_denoised_resid = reshape(sig1_denoised_resid,nImgs,nTrials-binr);
sig2_denoised_resid = reshape(sig2_denoised_resid,nImgs,nTrials-binr);

if binr ~= 0
    sig1_denoised_resid_r=reshape(sig1_denoised_resid_r,nImgs,binr);
    sig2_denoised_resid_r=reshape(sig2_denoised_resid_r,nImgs,binr);
    
    sig1_denoised_resid = cat(2,sig1_denoised_resid,sig1_denoised_resid_r);
    sig2_denoised_resid = cat(2,sig2_denoised_resid,sig2_denoised_resid_r);
end

sig1_br_resid=reshape(sig1_br_resid,nImgs,nTrials-binr);
sig2_br_resid=reshape(sig2_br_resid,nImgs,nTrials-binr);
sig1_pr_resid=reshape(sig1_pr_resid,nImgs,nTrials-binr);
sig2_pr_resid=reshape(sig2_pr_resid,nImgs,nTrials-binr);

if binr ~= 0
    sig1_br_resid_r=reshape(sig1_br_resid_r,nImgs,binr);
    sig2_br_resid_r=reshape(sig2_br_resid_r,nImgs,binr);
    sig1_pr_resid_r=reshape(sig1_pr_resid_r,nImgs,binr);
    sig2_pr_resid_r=reshape(sig2_pr_resid_r,nImgs,binr);
    
    sig1_br_resid=cat(2,sig1_br_resid,sig1_br_resid_r);
    sig2_br_resid=cat(2,sig2_br_resid,sig2_br_resid_r);
    sig1_pr_resid=cat(2,sig1_pr_resid,sig1_pr_resid_r);
    sig2_pr_resid=cat(2,sig2_pr_resid,sig2_pr_resid_r);
end

% The final outputs of this code are a Images x Trials matrix (fully
% processed) in the variables sig1_denoised_resid and sig2_denoised_resid.
% The following section of
% code will clear all the other variables. Please comment out this code if
% you intend to any sort of bug checking etc.

clear sig2_pr_resid_r sig1_pr_resid_r sig2_br_resid_r sig1_br_resid_r...
    nVec_sig2_r nVec_sig1_r nVec_sig2 nVec_sig1 std1_dn_r std2_dn_r...
    std1_dn std2_dn corrsigbr_r1 corrsigbr_r2 corrsigpr_r1 corrsigpr_r2...
    std1_b std1_p std2_b std2_p std1_b_r std1_p_r std2_b_r std2_p_r...
    nVec_sig1_b nVec_sig1_p nVec_sig2_b nVec_sig2_p numfiles nTrials nImgs...
    i k fpath file binr binsize sig1_br_r1 sig2_br_r1 sig1_pr_r1 sig2_pr_r1...
    sig1_br_resid sig2_br_resid sig1_pr_resid sig2_pr_resid sig1_denoised_resid_r...
    sig2_denoised_resid_r MMcorrsigbr MMcorrsigpr MMsig1_br MMsig1_pr MMsig2_br MMsig2_pr...
    MMsig1_br_resid MMsig1_pr_resid MMsig2_br_resid MMsig2_pr_resid

%% Below this point
% All the code below this point should be focused on analyzing the output
% of the earlier code, specifically the processed data stored in the output
% "sig1_denoised_resid" and "sig2_denoised_resid" variables, followed by a
% command to save the desired output data.

%% Analysis: Cross Correlation between Sig1 and Sig2

%% The End
% This code should always remain at the end. It merely prints done!
fprintf('done!\n')