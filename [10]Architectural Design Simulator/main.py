import tkinter as tk
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import Point3, Vec3, AmbientLight, DirectionalLight
from panda3d.bullet import BulletWorld, BulletRigidBodyNode, BulletPlaneShape
import math
import random

class ArchitecturalSimulator(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # カメラの初期設定
        self.camera.setPos(0, -50, 20) 
        self.camera.lookAt(Point3(0, 0, 0))

        # 光源の設定
        self.setup_lights()
        
        # 物理演算の設定
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))

        # 地面の物理設定
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        node = BulletRigidBodyNode('Ground')
        node.addShape(shape)
        np = self.render.attachNewNode(node)
        np.setPos(0, 0, 0)
        self.world.attachRigidBody(node)

        # 建物モデルの読み込みと物理設定
        self.building = self.loader.loadModel("models/building")
        self.building.reparentTo(self.render)
        self.building.setScale(1, 1, 1)
        self.building.setPos(0, 0, 0)
        
        # 建物の物理ボディ
        self.building_node = BulletRigidBodyNode('building')
        self.building_node.setMass(1000.0)
        self.building_np = self.render.attachNewNode(self.building_node)
        self.building.reparentTo(self.building_np)
        self.world.attachRigidBody(self.building_node)

        # カメラコントロールの設定
        self.setup_camera_control()

        # 災害シミュレーション設定
        self.disaster_active = False
        self.disaster_type = None
        self.disaster_intensity = 0.0

        # 災害コントロールの設定
        self.accept("e", self.start_earthquake)  # E キーで地震開始
        self.accept("t", self.start_tsunami)     # T キーで津波開始
        self.accept("escape", self.stop_disaster) # ESC キーで災害停止

        # 更新タスクの追加
        self.taskMgr.add(self.update, "updateTask")

    def setup_lights(self):
        # 環境光
        alight = AmbientLight('alight')
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        # 太陽光
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.8, 0.8, 0.8, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(45, -45, 0)
        self.render.setLight(dlnp)

    def setup_camera_control(self):
        # カメラ操作の設定
        self.accept("arrow_left", self.rotate_camera, [-1])
        self.accept("arrow_right", self.rotate_camera, [1])
        self.accept("arrow_up", self.zoom_camera, [-1])
        self.accept("arrow_down", self.zoom_camera, [1])

    def rotate_camera(self, direction):
        current_pos = self.camera.getPos()
        angle = math.radians(2 * direction)
        x = current_pos.x * math.cos(angle) - current_pos.y * math.sin(angle)
        y = current_pos.x * math.sin(angle) + current_pos.y * math.cos(angle)
        self.camera.setPos(x, y, current_pos.z)
        self.camera.lookAt(Point3(0, 0, 0))

    def zoom_camera(self, direction):
        current_pos = self.camera.getPos()
        zoom_factor = 1.1
        if direction < 0:
            self.camera.setPos(current_pos * zoom_factor)
        else:
            self.camera.setPos(current_pos / zoom_factor)

    def start_earthquake(self):
        self.disaster_active = True
        self.disaster_type = "earthquake"
        self.disaster_intensity = random.uniform(0.5, 2.0)
        print("地震シミュレーション開始: 震度", self.disaster_intensity)

    def start_tsunami(self):
        self.disaster_active = True
        self.disaster_type = "tsunami"
        self.disaster_intensity = random.uniform(1.0, 5.0)
        print("津波シミュレーション開始: 波高", self.disaster_intensity, "m")

    def stop_disaster(self):
        self.disaster_active = False
        self.disaster_type = None
        self.disaster_intensity = 0.0
        print("災害シミュレーション停止")

    def simulate_earthquake(self, dt):
        # 地震の揺れをシミュレート
        shake_x = math.sin(globalClock.getFrameTime() * 10) * self.disaster_intensity
        shake_y = math.cos(globalClock.getFrameTime() * 8) * self.disaster_intensity
        self.building_node.setAngularVelocity(Vec3(shake_x, shake_y, 0))

    def simulate_tsunami(self, dt):
        # 津波の力をシミュレート
        wave_force = Vec3(self.disaster_intensity * 5, 0, 0)
        self.building_node.applyCentralForce(wave_force)

    def update(self, task):
        dt = globalClock.getDt()
        
        if self.disaster_active:
            if self.disaster_type == "earthquake":
                self.simulate_earthquake(dt)
            elif self.disaster_type == "tsunami":
                self.simulate_tsunami(dt)
                
        self.world.doPhysics(dt)
        return Task.cont

# シミュレーション開始
sim = ArchitecturalSimulator()
sim.run()
