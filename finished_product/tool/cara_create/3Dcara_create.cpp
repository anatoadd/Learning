#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <vector>
#include <string>
#include <stdexcept>
#include <fstream>
#include <map>
#include <unordered_map>
#include <GLFW/glfw3.h>
#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>

// パーツ情報を管理する構造体
struct PartData {
    std::vector<cv::Point3f> vertices;
    std::vector<std::vector<int>> faces;
    std::vector<cv::Vec3f> normals;
    int sampleCount; // このパーツのデータ数
    float confidence; // 信頼度(データ数に基づく)
};

class Character3DCreator {
private:
    std::unordered_map<std::string, PartData> parts; // パーツごとのデータ
    std::vector<cv::Mat> depthMaps;
    std::vector<cv::Mat> normalMaps;
    cv::Mat finalDepthMap;
    cv::Mat finalNormalMap;
    bool hasExistingData;
    GLFWwindow* window;

    // パーツの定義
    const std::vector<std::string> partNames = {
        "head", "body", "right_arm", "left_arm", 
        "right_hand", "left_hand", "right_leg", "left_leg",
        "right_foot", "left_foot"
    };

public:
    Character3DCreator() : hasExistingData(false) {
        // GLFWの初期化
        if (!glfwInit()) {
            throw std::runtime_error("GLFWの初期化に失敗しました。");
        }

        // OpenGL 3.0 + GLSLを使用
        const char* glsl_version = "#version 130";
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);

        // ウィンドウの作成
        window = glfwCreateWindow(1280, 720, "3Dキャラクタークリエーター", NULL, NULL);
        if (window == NULL) {
            glfwTerminate();
            throw std::runtime_error("ウィンドウの作成に失敗しました。");
        }

        glfwMakeContextCurrent(window);
        glfwSwapInterval(1); // VSyncを有効化

        // ImGuiの初期化
        IMGUI_CHECKVERSION();
        ImGui::CreateContext();
        ImGui::StyleColorsDark();
        ImGui_ImplGlfw_InitForOpenGL(window, true);
        ImGui_ImplOpenGL3_Init(glsl_version);

        // パーツの初期化
        for(const auto& partName : partNames) {
            parts[partName] = PartData();
            parts[partName].sampleCount = 0;
            parts[partName].confidence = 0.0f;
        }
    }

    ~Character3DCreator() {
        ImGui_ImplOpenGL3_Shutdown();
        ImGui_ImplGlfw_Shutdown();
        ImGui::DestroyContext();
        glfwDestroyWindow(window);
        glfwTerminate();
    }

    void renderUI() {
        while (!glfwWindowShouldClose(window)) {
            glfwPollEvents();

            ImGui_ImplOpenGL3_NewFrame();
            ImGui_ImplGlfw_NewFrame();
            ImGui::NewFrame();

            // メインウィンドウ
            ImGui::Begin("3Dキャラクタークリエーター");

            if (ImGui::Button("モデルを読み込む")) {
                try {
                    loadExistingModel("previous_model.obj");
                } catch (const std::exception& e) {
                    ImGui::OpenPopup("エラー");
                }
            }

            if (ImGui::Button("モデルを保存")) {
                try {
                    exportToObj("output_model.obj");
                } catch (const std::exception& e) {
                    ImGui::OpenPopup("エラー");
                }
            }

            // パーツ情報の表示
            ImGui::Text("パーツ情報:");
            for (const auto& [partName, partData] : parts) {
                ImGui::Text("%s: サンプル数 %d, 信頼度 %.2f", 
                    partName.c_str(), partData.sampleCount, partData.confidence);
            }

            ImGui::End();

            // エラーポップアップ
            if (ImGui::BeginPopupModal("エラー", NULL, ImGuiWindowFlags_AlwaysAutoResize)) {
                ImGui::Text("処理中にエラーが発生しました。");
                if (ImGui::Button("OK")) {
                    ImGui::CloseCurrentPopup();
                }
                ImGui::EndPopup();
            }

            ImGui::Render();
            int display_w, display_h;
            glfwGetFramebufferSize(window, &display_w, &display_h);
            glViewport(0, 0, display_w, display_h);
            glClearColor(0.45f, 0.55f, 0.60f, 1.00f);
            glClear(GL_COLOR_BUFFER_BIT);
            ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

            glfwSwapBuffers(window);
        }
    }

    void loadExistingModel(const std::string& objFile) {
        std::ifstream in(objFile);
        if(!in.is_open()) {
            throw std::runtime_error("既存モデルを読み込めませんでした。");
        }

        std::string currentPart;
        std::string line;
        
        while(std::getline(in, line)) {
            if(line.substr(0,2) == "# ") {
                // パーツ情報の読み込み
                std::string info = line.substr(2);
                size_t pos = info.find(":");
                if(pos != std::string::npos) {
                    currentPart = info.substr(0, pos);
                    sscanf(info.substr(pos+1).c_str(), "%d %f", 
                           &parts[currentPart].sampleCount,
                           &parts[currentPart].confidence);
                }
            }
            else if(line[0] == 'v' && line[1] == ' ') {
                float x, y, z;
                sscanf(line.c_str(), "v %f %f %f", &x, &y, &z);
                if(!currentPart.empty()) {
                    parts[currentPart].vertices.push_back(cv::Point3f(x, y, z));
                }
            }
            else if(line[0] == 'v' && line[1] == 'n') {
                float nx, ny, nz;
                sscanf(line.c_str(), "vn %f %f %f", &nx, &ny, &nz);
                if(!currentPart.empty()) {
                    parts[currentPart].normals.push_back(cv::Vec3f(nx, ny, nz));
                }
            }
            else if(line[0] == 'f') {
                std::vector<int> face;
                std::stringstream ss(line.substr(2));
                std::string vertex;
                while(ss >> vertex) {
                    face.push_back(std::stoi(vertex.substr(0, vertex.find("//"))) - 1);
                }
                if(!currentPart.empty()) {
                    parts[currentPart].faces.push_back(face);
                }
            }
        }
        
        hasExistingData = true;
        in.close();
    }

    void exportToObj(const std::string& filename) {
        std::ofstream out(filename);
        if(!out.is_open()) {
            throw std::runtime_error("ファイルを開けませんでした。");
        }

        int vertexOffset = 0;
        
        for(const auto& [partName, partData] : parts) {
            // パーツ情報のヘッダー出力
            out << "# " << partName << ": " 
                << partData.sampleCount << " " 
                << partData.confidence << "\n";

            // 頂点と法線の出力
            for(size_t i = 0; i < partData.vertices.size(); i++) {
                const auto& v = partData.vertices[i];
                const auto& n = partData.normals[i];
                out << "v " << v.x << " " << v.y << " " << v.z << "\n";
                out << "vn " << n[0] << " " << n[1] << " " << n[2] << "\n";
            }

            // 面の出力
            for(const auto& f : partData.faces) {
                out << "f";
                for(int idx : f) {
                    out << " " << (idx + vertexOffset + 1) << "//" << (idx + vertexOffset + 1);
                }
                out << "\n";
            }

            vertexOffset += partData.vertices.size();
        }

        out.close();
    }

    float calculateWeight(const std::string& partName) {
        const auto& part = parts[partName];
        if(part.sampleCount == 0) return 1.0f;
        return 1.0f / (1.0f + std::log(part.sampleCount + 1));
    }
};

int main() {
    try {
        Character3DCreator creator;
        creator.renderUI();
        return 0;
    } catch(const std::exception& e) {
        std::cerr << "エラーが発生しました: " << e.what() << std::endl;
        return -1;
    }
}
