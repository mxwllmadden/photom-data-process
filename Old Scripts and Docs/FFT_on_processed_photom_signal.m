
clear
motherpath = uigetdir('','Select the Properly Formatted Cohort Folder'); % Get the cohort directory
mpathrawlist = dir(motherpath);
mpath = {};
ping = "Ping!";

for i = 3:sum(arrayfun(@(mpathrawlist) ~isempty(mpathrawlist.name),mpathrawlist)) % Iterate through the folders present in the cohort directory
    if mpathrawlist(i).isdir == 0
        g = append(mpathrawlist(i).folder,'\',mpathrawlist(i).name);
        mpath = [mpath g]; % Store the paths of all the animal names in the cohort directory
        AnimalName{i} = mpathrawlist(i).name;
    end
end
for i = 3:numel(AnimalName)
    aname{i-2} = AnimalName{i};
end
AnimalName = aname;
clear motherpath g i aname;
PTA_Animal = {};
PLPFC_Animal = {};

for i = 1:numel(mpath)
    if contains(mpath{i},'Master') ~= 1
        PTA_Animal{i} = xlsread(mpath{i},"PTA");
        PLPFC_Animal{i} = xlsread(mpath{i},"PLPFC");
        PTA_BeforeStim{i} = PTA_Animal{i}(1:1350,:);
        PTA_AfterStim{i} = PTA_Animal{i}(1651:3000,:);
        PLPFC_BeforeStim{i} = PLPFC_Animal{i}(1:1350,:);
        PLPFC_AfterStim{i} = PLPFC_Animal{i}(1651:3000,:);
        
    end
end

Fs = 10; %10 Hz recording
T = 1/Fs;
L = 1350; %length of signal
t = (0:L-1)*T;


% For Testing
% for i = 1:numel(PTA_BeforeStim)
%     if numel(PTA_BeforeStim{i}) ~= 0
%         S = 0.7*sin(2*pi*1*t) + sin(2*pi*0.4*t);
%         S1 = (PTA_BeforeStim{i}(1,:) * 0) + 1;
%         S = S'.*S1;
%         PTA_BeforeStim{i} = (PTA_BeforeStim{i} * 0) + 1;
%         PTA_BeforeStim{i} = PTA_BeforeStim{i} .* S;
%     end
% end

%next step: run the FFT
for i = 1:numel(mpath)
    if numel(PTA_AfterStim{i}) ~= 0
        for j = 1:numel(PTA_AfterStim{i}(1,:))
            %Run FFT
            FFT_PTA_BeforeStim{i} = fft(PTA_BeforeStim{i});
            FFT_PTA_AfterStim{i} = fft(PTA_AfterStim{i});
            FFT_PLPFC_BeforeStim{i} = fft(PLPFC_BeforeStim{i});
            FFT_PLPFC_AfterStim{i} = fft(PLPFC_AfterStim{i});

            %Now we have to calculate magnitudes from the FFT data
            P2_PTA_BeforeStim{i} = abs(FFT_PTA_BeforeStim{i}/L);
            P2_PTA_AfterStim{i} = abs(FFT_PTA_AfterStim{i}/L);
            P2_PLPFC_BeforeStim{i} = abs(FFT_PLPFC_BeforeStim{i}/L);
            P2_PLPFC_AfterStim{i} = abs(FFT_PLPFC_AfterStim{i}/L);
            
            %
            P1_PTA_BeforeStim{i} = P2_PTA_BeforeStim{i}(1:L/2+1,:);
            P1_PTA_BeforeStim{i}(2:end-1,:) = 2*P1_PTA_BeforeStim{i}(2:end-1,:);
            P1_PTA_AfterStim{i} = P2_PTA_AfterStim{i}(1:L/2+1,:);
            P1_PTA_AfterStim{i}(2:end-1,:) = 2*P1_PTA_AfterStim{i}(2:end-1,:);
            P1_PLPFC_BeforeStim{i} = P2_PLPFC_BeforeStim{i}(1:L/2+1,:);
            P1_PLPFC_BeforeStim{i}(2:end-1,:) = 2*P1_PLPFC_BeforeStim{i}(2:end-1,:);
            P1_PLPFC_AfterStim{i} = P2_PLPFC_AfterStim{i}(1:L/2+1,:);
            P1_PLPFC_AfterStim{i}(2:end-1,:) = 2*P1_PLPFC_AfterStim{i}(2:end-1,:);
            
            %Averageing of Individual Data
            AvP1_PTA_BeforeStim(:,i) = mean(P1_PTA_BeforeStim{i},2);
            AvP1_PTA_AfterStim(:,i) = mean(P1_PTA_AfterStim{i},2);
            AvP1_PLPFC_BeforeStim(:,i) = mean(P1_PLPFC_BeforeStim{i},2);
            AvP1_PLPFC_AfterStim(:,i) = mean(P1_PLPFC_AfterStim{i},2);
        end
    end
end
