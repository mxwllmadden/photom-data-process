%% Photometry Data Validation Tool
% This script is meant to create "Spoofed" output that can be processed and
% compared to expected results

tempM = ones(200,30);
f = .05:.05:10;
sign = sin(f');
sign = sign * 100;

tempM = reshape(tempM,200*30,1);
tempM = tempM - [0.00001666666:0.00001666666:.1]';
tempM = reshape(tempM,200,30);
% Set everything to zero; true control condition
corrsigbr = (tempM * 10);
corrsigpr = (tempM * 150);
sig1_br = (tempM * 20) + ;
sig1_pr = (tempM * 1200) + sign;
sig2_br = (tempM * 20);
sig2_pr = (tempM * 1200) + (sign*.0000001);



sig1_br_resid = tempM * 0;
sig1_pr_resid = tempM * 0;
sig2_br_resid = tempM * 0;
sig2_pr_resid = tempM * 0;
sig2_str = 'Signal 2';
sig1_str = 'Signal 1';
for i = 1:4
    fname = ['test',num2str(i),'.mat'];
    save(fname,'corrsigbr','sig2_str','sig1_str','corrsigpr','sig1_br','sig1_pr','sig2_br','sig2_pr','sig1_br_resid','sig1_pr_resid','sig2_br_resid','sig2_pr_resid')
end
% corrsigbr =
% corrsigpr =
% sig1_br =
% sig1_pr =
% sig2_br =
% sig2_pr =