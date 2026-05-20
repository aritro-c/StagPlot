clear; clc;

% Export Options
export_plot = true; % Set to true to save the plot
fig_width = 12;     % Width in inches
fig_height = 6;     % Height in inches
output_name = "Surface_Mobility_Plot.svg";

data1 = readtable("noGI_plates_analyse.dat");
data2 = readtable("noGI_plates_analyse_i.dat");

time1 = (data1.x_time)/(60*60*24*365*1e9) ;
time2 = (data2.x_time)/(60*60*24*365*1e9) ;

mob1 = data1.x_Mob;
mob2 = data2.x_Mob;


fig = figure("Name","Surface Mobility");

plot(time1,mob1,"LineWidth",2,"Color","blue"); hold on;
plot(time2,mob2, "LineWidth", 2,"Color","red");

xlabel("Time (Gyr)","FontSize",16,"FontName","Arial");
ylabel("Surface Mobility", "FontSize",16, "FontName","Arial")
lgd = legend("Without LA Impacts","With LA Impacts","FontSize",16, "FontName","Arial");
set(lgd, 'Color', 'none'); % Set legend background to transparent
xlim([0 4.5]);
set(gca, 'FontSize', 18, 'LineWidth', 1); % Decreased font size, increased border width

% Transparency and Export settings (Replicating reference script logic)
if export_plot
    fprintf('Exporting plot to %s...\n', output_name);

    % --- SIZE CONTROL ---
    set(fig, 'Units', 'inches', 'Position', [1, 1, fig_width, fig_height]);
    set(fig, 'PaperUnits', 'inches', 'PaperPosition', [0, 0, fig_width, fig_height]);
    set(fig, 'PaperSize', [fig_width, fig_height]);

    % --- TRANSPARENCY & RENDERER ---
    set(fig, 'Color', 'none');
    set(gca, 'Color', 'none');
    set(fig, 'InvertHardcopy', 'off');
    set(fig, 'Renderer', 'painters');

    % --- PRINT ---
    print(fig, char(output_name), '-dsvg', '-painters');

    fprintf('SVG exported at %.1f x %.1f inches: %s\n', fig_width, fig_height, output_name);
end