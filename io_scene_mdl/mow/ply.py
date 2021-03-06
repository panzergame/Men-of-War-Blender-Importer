# Initial version of this file by Stan Bobovych
# The original version can be found here https://github.com/sbobovyc/GameTools/blob/master/MoW/ply.py

# Further enhancements modifications by Björn Martins Paz

from __future__ import print_function

import struct
import sys

from ply_mesh import PLY_MESH

# constants
PLYMAGICK = b"EPLY"

D3DFVF_RESERVED0 = 0x01
D3DFVF_POSITION_MASK = 0x4000E
D3DFVF_XYZ = 0x02
D3DFVF_XYZRHW = 0x04
D3DFVF_XYZB1 = 0x06
D3DFVF_XYZB2 = 0x08
D3DFVF_XYZB3 = 0x0a
D3DFVF_XYZB4 = 0x0c
D3DFVF_XYZB5 = 0x0e
D3DFVF_XYZW = 0x4002
D3DFVF_NORMAL = 0x10
D3DFVF_PSIZE = 0x20
D3DFVF_DIFFUSE = 0x40
D3DFVF_SPECULAR = 0x80
D3DFVF_TEXCOUNT_MASK = 0xf00
D3DFVF_TEXCOUNT_SHIFT = 8
D3DFVF_TEX0 = 0x0000
D3DFVF_TEX1 = 0x0100
D3DFVF_TEX2 = 0x0200
D3DFVF_TEX3 = 0x0300
D3DFVF_TEX4 = 0x0400
D3DFVF_TEX5 = 0x0500
D3DFVF_TEX6 = 0x0600
D3DFVF_TEX7 = 0x0700
D3DFVF_TEX8 = 0x0800
D3DFVF_TEXTUREFORMAT1 = 3
D3DFVF_TEXTUREFORMAT2 = 0
D3DFVF_TEXTUREFORMAT3 = 1
D3DFVF_TEXTUREFORMAT4 = 2
D3DFVF_LASTBETA_UBYTE4 = 0x1000
D3DFVF_LASTBETA_D3DCOLOR = 0x8000
D3DFVF_RESERVED2 = 0x6000

MESH_FLAG_TWO_SIDED = 0b1 # render this mesh without culling
MESH_FLAG_USE_ALPHA = 0b10 # (unused, compatibility mode)
MESH_FLAG_LIGHT     = 0b100 # use realtime scene light (unused, compatibility mode)
MESH_FLAG_PLCR      = 0b1000 # use player color light
MESH_FLAG_SKINNED   = 0b10000 # skinned mesh
MESH_FLAG_SHADOW    = 0b100000 # shadow volume mesh
MESH_FLAG_MIRRORED  = 0b1000000 # has negative scaling
MESH_FLAG_BLENDTEX  = 0b10000000 # blend by second texture alpha
MESH_FLAG_BUMP      = 0b100000000 # bump-mapped
MESH_FLAG_SPECULAR  = 0b1000000000 # specular color stored
MESH_FLAG_MATERIAL  = 0b10000000000 # format with material, not textures
MESH_FLAG_SUBSKIN   = 0b100000000000 # sub-skin feature
MESH_FLAG_TWOTEX    = 0b1000000000000 # two textures with one texcoord
MESH_FLAG_USINGVD   = 0b10000000000000 # using vertex declaration instead of fvf
MESH_FLAG_LIGHTMAP  = 0b100000000000000 # has lightmap

class PLY:
    def __init__(self, path):
        self.path = path
        self.indices = []
        self.positions = []
        self.weights = []
        self.matrix_indices = []
        self.normals = []
        self.UVs = []

        self.mesh_fvf = None # Vertex format of the first mesh
        self.mesh_flags = None # Flags of the first mesh

        self.meshes = []

        self.open(self.path)

    def open(self, peek=False, verbose=False):
        with open(self.path, "rb") as f:
            # Read file header ID
            magick, = struct.unpack("4s", f.read(4))
            if magick != PLYMAGICK:
                raise Exception("Unsupported format %s" % magick)

            # Read all data chunks
            while True:
                # Read next data chunk ID
                try:
                    entry, = struct.unpack("4s", f.read(4))
                except:
                    break

                print("Found data chunk %s at %s" % (entry, hex(f.tell())) )

                # try to call the apropriate method to handle this chunk of data
                try:
                    chunk_method = entry.decode().lower()
                    getattr(self, chunk_method)(f)
                except AttributeError:
                    raise Exception("Unsupported data chunk")

    def bnds(self, f):
        # read bounding box coordinates
        x1, y1, z1, x2, y2, z2 = struct.unpack("ffffff", f.read(24))

    def skin(self, f):
        # read the skin mesh bone data
        bones, = struct.unpack("<I", f.read(4))
        print("Number of skin bones: %i at %s" % (bones, hex(f.tell())))
        for i in range(0, bones):
          bone_name_length, = struct.unpack("B", f.read(1))
          #print("Bone name length:", hex(bone_name_length))
          bone_name = f.read(bone_name_length)
          bone_name = bone_name.decode()
          print("Bone name:", bone_name)

    def mesh(self, f):
        ply_mesh = PLY_MESH()

        ply_mesh.fvf,        = struct.unpack("<I", f.read(4))
        ply_mesh.first_face, = struct.unpack("<I", f.read(4))
        ply_mesh.face_count, = struct.unpack("<I", f.read(4))
        ply_mesh.flags,      = struct.unpack("<I", f.read(4))

        print("------------ Mesh Flags -----------")
        print("MESH_FLAG_TWO_SIDED = ", ply_mesh.flags & MESH_FLAG_TWO_SIDED )
        print("MESH_FLAG_USE_ALPHA = ", ply_mesh.flags & MESH_FLAG_USE_ALPHA )
        print("MESH_FLAG_LIGHT     = ", ply_mesh.flags & MESH_FLAG_LIGHT )
        print("MESH_FLAG_PLCR      = ", ply_mesh.flags & MESH_FLAG_PLCR )
        print("MESH_FLAG_SKINNED   = ", ply_mesh.flags & MESH_FLAG_SKINNED )
        print("MESH_FLAG_SHADOW    = ", ply_mesh.flags & MESH_FLAG_SHADOW )
        print("MESH_FLAG_MIRRORED  = ", ply_mesh.flags & MESH_FLAG_MIRRORED )
        print("MESH_FLAG_BLENDTEX  = ", ply_mesh.flags & MESH_FLAG_BLENDTEX )
        print("MESH_FLAG_BUMP      = ", ply_mesh.flags & MESH_FLAG_BUMP )
        print("MESH_FLAG_SPECULAR  = ", ply_mesh.flags & MESH_FLAG_SPECULAR )
        print("MESH_FLAG_MATERIAL  = ", ply_mesh.flags & MESH_FLAG_MATERIAL )
        print("MESH_FLAG_SUBSKIN   = ", ply_mesh.flags & MESH_FLAG_SUBSKIN )
        print("MESH_FLAG_TWOTEX    = ", ply_mesh.flags & MESH_FLAG_TWOTEX )
        print("MESH_FLAG_USINGVD   = ", ply_mesh.flags & MESH_FLAG_USINGVD )
        print("MESH_FLAG_LIGHTMAP  = ", ply_mesh.flags & MESH_FLAG_LIGHTMAP )
        print("-----------------------------------")

        self.mesh_fvf = ply_mesh.fvf
        self.mesh_flags = ply_mesh.flags

        print("Flexible Vertex Format:", hex(ply_mesh.fvf))
        print("First face:", ply_mesh.first_face)
        print("Number of faces:", ply_mesh.face_count)
        print("Mesh flags:", hex(ply_mesh.flags))

        # Check if there is specular color data to be read
        if ply_mesh.flags & MESH_FLAG_SPECULAR:
            ply_mesh.rgba_color = f.read(0x4) # R G B A

        # Check if there is material file data to be read
        if ply_mesh.flags & MESH_FLAG_MATERIAL:
            ply_mesh.material_filename_length, = struct.unpack("B", f.read(1))
            ply_mesh.material_file = f.read(ply_mesh.material_filename_length)
            ply_mesh.material_file = ply_mesh.material_file.decode("utf-8")
            print("Material file name length:", ply_mesh.material_filename_length)
            print("Material file:", ply_mesh.material_file)
        else:
            raise Exception("Old unsupported PLY format")

        # Check if sub-skin data is present
        if ply_mesh.flags & MESH_FLAG_SUBSKIN:
            print("Reading subskin data")
            ply_mesh.subskin_count, = struct.unpack("B", f.read(1))
            for i in range(0, ply_mesh.subskin_count):
                ply_mesh.subskin_bones.append(struct.unpack("B", f.read(1)))

        self.meshes.append(ply_mesh)

    def vert(self, f):
        vertex_count, = struct.unpack("<I", f.read(4))
        vertex_size, = struct.unpack("<H", f.read(2))
        self.vertex_flags, = struct.unpack("<H", f.read(2))

        has_pos = False
        has_rhw = False
        has_weights = False
        num_weights = 0
        has_matrix_indices = False
        has_normal = False
        has_psize = False
        has_diffuse = False
        has_specular = False
        has_tex_coords = False
        num_tex_coords = 0
        has_d3d_color = False

        # Decode the D3D9 Flexible Vertex Format flags of this mesh
        has_pos      = ((self.mesh_fvf & D3DFVF_POSITION_MASK) != 0)
        has_rhw      = ((self.mesh_fvf & D3DFVF_POSITION_MASK) == D3DFVF_XYZRHW)
        has_weights  = ((self.mesh_fvf & D3DFVF_XYZB5) >= D3DFVF_XYZB1)
        if has_weights:
            num_weights = 1 + (((self.mesh_fvf & D3DFVF_XYZB5) - D3DFVF_XYZB1) >> 1)
        if has_weights:
            has_matrix_indices = (((self.mesh_fvf & D3DFVF_XYZB5) == D3DFVF_XYZB5) or ((self.mesh_fvf & D3DFVF_LASTBETA_D3DCOLOR) != 0) or ((self.mesh_fvf & D3DFVF_LASTBETA_UBYTE4) != 0));
            num_weights -= 1
        has_normal   = ((self.mesh_fvf & D3DFVF_NORMAL) != 0)
        has_psize    = ((self.mesh_fvf & D3DFVF_PSIZE) != 0)
        has_diffuse  = ((self.mesh_fvf & D3DFVF_DIFFUSE) != 0)
        has_specular = ((self.mesh_fvf & D3DFVF_SPECULAR) != 0)
        has_tex_coords = ((self.mesh_fvf & D3DFVF_TEXCOUNT_MASK) != 0)
        if has_tex_coords:
            num_tex_coords = (self.mesh_fvf & D3DFVF_TEXCOUNT_MASK) >> D3DFVF_TEXCOUNT_SHIFT

        has_mesh_specular = ((self.mesh_flags & MESH_FLAG_SPECULAR) != 0)
        has_mesh_bump = ((self.mesh_flags & MESH_FLAG_BUMP) != 0)

        print("Vertex size:", vertex_size)
        print("Vertex count:", vertex_count)
        print("Vertex flags:", hex(self.vertex_flags))
        print("------------ D3D9 FVF -----------")
        print("FVF flags:", hex(self.mesh_fvf))
        print("Has position:", has_pos)
        print("Has RHW:", has_rhw)
        print("Has weights:", has_weights)
        print("Num weights:", num_weights)
        print("Has matrix indices:", has_matrix_indices)
        print("Has normal:", has_normal)
        print("Has psize:", has_psize)
        print("Has diffuse:", has_diffuse)
        print("Has specular:", has_specular)
        print("Has tex coords:", has_tex_coords)
        print("Num tex coords:", num_tex_coords)
        print("---------------------------------")
        print("Has mesh specular:", has_mesh_specular)

        # Read the vertices
        for i in range(0, vertex_count):
            if has_pos:
                vx, vy, vz = struct.unpack("fff", f.read(12))
                self.positions.append([vx,vy,vz])

            if has_rhw:
                f.read(4)

            if has_weights and num_weights > 0:
                weights = []
                for i in range(0, num_weights):
                    weight, = struct.unpack("f", f.read(4))
                    weights.append(weight)
                self.weights.append(weights)

            if has_matrix_indices:
                # matrix_indices, = struct.unpack("<I", f.read(4))
                index1, index2, index3, index4 = struct.unpack("<BBBB", f.read(4))
                # self.matrix_indices.append(matrix_indices)

            if has_normal:
                nx, ny, nz = struct.unpack("fff", f.read(12))
                self.normals.append((nx,ny,nz))

            if has_psize:
                f.read(4)

            if has_diffuse:
                f.read(4)

            if has_specular:
                f.read(4)

            if has_tex_coords and num_tex_coords > 0:
                U,V = struct.unpack("ff", f.read(8))
                self.UVs.append((U,1-V))
                # We don't handle more than one texture coordinate at this time, so throw the others away
                f.read((num_tex_coords-1) * 8)

            # if has_mesh_specular:
            #     f.read(16)

            if has_mesh_bump:
                f.read(16)

    def indx(self, f):
        idx_count, = struct.unpack("<I", f.read(4))
        print("Indices:", idx_count)
        total_face_count = int(idx_count / 3)

        # Process each mesh
        for mesh in self.meshes:
            print("Mesh %s" % mesh.material_file)
            print("From %i to %i" % (mesh.first_face, mesh.first_face + mesh.face_count))
            for i in range(mesh.first_face, mesh.first_face + mesh.face_count):
                i0, i1, i2 = struct.unpack("<HHH", f.read(6))
                if self.mesh_flags & MESH_FLAG_MIRRORED:
                    self.indices.append((i0,i1,i2))
                    mesh.indices.append(i0)
                    mesh.indices.append(i1)
                    mesh.indices.append(i2)
                    mesh.weights.append(0)
                    mesh.weights.append(0)
                    mesh.weights.append(0)
                else:
                    self.indices.append((i2,i1,i0))
                    mesh.indices.append(i2)
                    mesh.indices.append(i1)
                    mesh.indices.append(i0)
                    mesh.weights.append(0)
                    mesh.weights.append(0)
                    mesh.weights.append(0)

    def mror(self, f):
        # for position in self.positions:
        #     position[0] = -position[0]
        pass

    def dump(self, outfile):
        print("Dumping to OBJ")
        with open(outfile, "wb") as f:
            for p in self.positions:
                f.write('{:s} {:f} {:f} {:f}\n'.format("v", *p))
            for UV in self.UVs:
                u = UV[0]
                v = 1.0 - UV[1]
                f.write('{:s} {:f} {:f}\n'.format("vt", u, v))
            for n in self.normals:
                f.write('{:s} {:f} {:f} {:f}\n'.format("vn", *n))
            for idx in self.indices:
                new_idx = map(lambda x: x+1, idx)
                # change vertex index order by swapping the first and last indices
                f.write('{:s} {:d}/{:d}/{:d} {:d}/{:d}/{:d} {:d}/{:d}/{:d}\n'.format("f", new_idx[2], new_idx[2],
                new_idx[2], new_idx[1], new_idx[1], new_idx[1], new_idx[0], new_idx[0], new_idx[0]))